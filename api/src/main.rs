//! Anonymous counters. Two endpoints, one table, integers only.
//!
//! What this service deliberately does not have: user ids, sessions, IP logging,
//! per-answer timestamps, and any column that could join two answers together.
//! Losing this database costs statistics and nothing else.

use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};

use axum::extract::State;
use axum::http::StatusCode;
use axum::routing::get;
use axum::{Json, Router};
use rusqlite::{params, Connection};
use serde::Deserialize;
use tower_http::cors::{Any, CorsLayer};

/// Likert scale width. Kept in step with CHOICES in web/src/lib/score.js.
const CHOICES: usize = 5;

#[derive(Clone)]
struct App {
    // ponytail: one global lock. These are single-row upserts on a tiny table;
    // move to a connection pool if a profile ever shows contention here.
    db: Arc<Mutex<Connection>>,
    questions: Arc<HashSet<String>>,
}

#[derive(Deserialize)]
struct Answer {
    question: String,
    choice: usize,
}

fn open(path: &str) -> rusqlite::Result<Connection> {
    let db = Connection::open(path)?;
    db.execute_batch(
        "PRAGMA journal_mode=WAL;
         CREATE TABLE IF NOT EXISTS counts (
             question TEXT    NOT NULL,
             choice   INTEGER NOT NULL,
             n        INTEGER NOT NULL DEFAULT 0,
             PRIMARY KEY (question, choice)
         ) WITHOUT ROWID;",
    )?;
    Ok(db)
}

/// The trust boundary: the request names a question and a choice, and both are
/// checked against content the client cannot influence. Without this an
/// attacker grows the table without bound by inventing question ids.
fn valid(questions: &HashSet<String>, answer: &Answer) -> bool {
    answer.choice < CHOICES && questions.contains(&answer.question)
}

fn bump(db: &Connection, question: &str, choice: usize) -> rusqlite::Result<()> {
    db.execute(
        "INSERT INTO counts (question, choice, n) VALUES (?1, ?2, 1)
         ON CONFLICT (question, choice) DO UPDATE SET n = n + 1",
        params![question, choice as i64],
    )?;
    Ok(())
}

/// Every known question, always the full scale, so the client sees a stable shape.
fn tally(db: &Connection, questions: &HashSet<String>) -> rusqlite::Result<HashMap<String, Vec<i64>>> {
    let mut out: HashMap<String, Vec<i64>> =
        questions.iter().map(|id| (id.clone(), vec![0; CHOICES])).collect();

    let mut statement = db.prepare("SELECT question, choice, n FROM counts")?;
    let rows = statement.query_map([], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, usize>(1)?, row.get::<_, i64>(2)?))
    })?;

    for row in rows {
        let (question, choice, n) = row?;
        if let Some(slot) = out.get_mut(&question).and_then(|row| row.get_mut(choice)) {
            *slot = n;
        }
    }
    Ok(out)
}

async fn post_count(State(app): State<App>, Json(answer): Json<Answer>) -> StatusCode {
    if !valid(&app.questions, &answer) {
        return StatusCode::BAD_REQUEST;
    }
    let db = app.db.lock().expect("counter lock");
    match bump(&db, &answer.question, answer.choice) {
        Ok(()) => StatusCode::NO_CONTENT,
        Err(_) => StatusCode::INTERNAL_SERVER_ERROR,
    }
}

async fn get_counts(State(app): State<App>) -> Result<Json<HashMap<String, Vec<i64>>>, StatusCode> {
    let db = app.db.lock().expect("counter lock");
    tally(&db, &app.questions)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

fn load_questions(path: &str) -> HashSet<String> {
    #[derive(Deserialize)]
    struct Question {
        id: String,
    }
    #[derive(Deserialize)]
    struct File {
        questions: Vec<Question>,
    }

    let text = std::fs::read_to_string(path)
        .unwrap_or_else(|error| panic!("cannot read {path}: {error}"));
    serde_json::from_str::<File>(&text)
        .unwrap_or_else(|error| panic!("cannot parse {path}: {error}"))
        .questions
        .into_iter()
        .map(|question| question.id)
        .collect()
}

fn env(key: &str, fallback: &str) -> String {
    std::env::var(key).unwrap_or_else(|_| fallback.to_string())
}

#[tokio::main]
async fn main() {
    let questions = load_questions(&env("CIVIS_QUESTIONS", "../content/questions/fr-2027.json"));
    let db = open(&env("CIVIS_DB", "civis.sqlite3")).expect("open database");
    let address = env("CIVIS_ADDR", "127.0.0.1:8787");

    let app = App {
        db: Arc::new(Mutex::new(db)),
        questions: Arc::new(questions),
    };

    // No credentials, no auth, no per-user data: anyone may read the aggregates
    // and add to them. Origin restrictions would protect nothing here.
    let cors = CorsLayer::new().allow_origin(Any).allow_methods(Any).allow_headers(Any);
    let router = Router::new()
        .route("/counts", get(get_counts).post(post_count))
        .layer(cors)
        .with_state(app);

    let listener = tokio::net::TcpListener::bind(&address).await.expect("bind");
    println!("counters on http://{address}");
    axum::serve(listener, router).await.expect("serve");
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture() -> (Connection, HashSet<String>) {
        let db = Connection::open_in_memory().unwrap();
        db.execute_batch(
            "CREATE TABLE counts (
                 question TEXT NOT NULL, choice INTEGER NOT NULL,
                 n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (question, choice)
             );",
        )
        .unwrap();
        (db, ["q-isf".to_string(), "q-ric".to_string()].into_iter().collect())
    }

    #[test]
    fn counts_accumulate_per_question_and_choice() {
        let (db, questions) = fixture();
        bump(&db, "q-isf", 4).unwrap();
        bump(&db, "q-isf", 4).unwrap();
        bump(&db, "q-isf", 0).unwrap();
        bump(&db, "q-ric", 2).unwrap();

        let counts = tally(&db, &questions).unwrap();
        assert_eq!(counts["q-isf"], vec![1, 0, 0, 0, 2]);
        assert_eq!(counts["q-ric"], vec![0, 0, 1, 0, 0]);
    }

    #[test]
    fn unanswered_questions_report_a_full_scale_of_zeroes() {
        let (db, questions) = fixture();
        let counts = tally(&db, &questions).unwrap();
        assert_eq!(counts.len(), 2);
        assert_eq!(counts["q-isf"], vec![0; CHOICES]);
    }

    #[test]
    fn unknown_questions_and_out_of_range_choices_are_rejected() {
        let (_db, questions) = fixture();
        let answer = |question: &str, choice: usize| Answer {
            question: question.to_string(),
            choice,
        };
        assert!(valid(&questions, &answer("q-isf", 0)));
        assert!(valid(&questions, &answer("q-isf", 4)));
        assert!(!valid(&questions, &answer("q-isf", 5)), "choice past the scale");
        assert!(!valid(&questions, &answer("made-up", 0)), "unknown question id");
    }

    #[test]
    fn a_row_written_outside_the_scale_cannot_corrupt_the_response() {
        let (db, questions) = fixture();
        db.execute(
            "INSERT INTO counts (question, choice, n) VALUES ('q-isf', 99, 7)",
            [],
        )
        .unwrap();
        let counts = tally(&db, &questions).unwrap();
        assert_eq!(counts["q-isf"], vec![0; CHOICES]);
    }
}
