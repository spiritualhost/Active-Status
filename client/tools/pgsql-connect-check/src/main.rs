//Use this tool to check the connection to the postgresql server from a .env file
//Useful for troubleshooting why a specific endpoint has connection issues
use std::path::PathBuf;
use std::{process, env};
use postgres::{Client, Config, Error, NoTls};
use rfd::FileDialog;
use dotenvy;

fn attempt_pgsql_connection(database: &str, user: &str, password: &str, host: &str, port: u16) -> Result<Client, Error> {
    //Make a connection to the pgsql server
    let client = Config::new()
        .host(host)
        .port(port)
        .user(user)
        .password(password)
        .dbname(database)
        .connect(NoTls)?;

    //Return the active client
    Ok(client)
}

fn main() {
    println!("Opening file explorer...");

    //Opens file explorer to select a file
    let selected_path: Option<PathBuf> = FileDialog::new()
        .set_title("Select an Active Status .env file")
        .set_directory("/")
        .add_filter("Environment Files", &["env"])
        .pick_file();

    let env_path: PathBuf = match selected_path {
        Some(path) => path,
        None => process::exit(1),
    };

    //Load the .env file, using .ok() ignores errors if the file is missing
    dotenvy::from_path(env_path).ok();

    //Read variables into memory (returns a Result<String, VarError>)
    let database = env::var("DATABASE").expect("Database value must be set");
    let user = env::var("USER").expect("User value must be set");
    let password = env::var("PASSWORD").expect("Password value must be set");
    let host = env::var("HOST").expect("Host value must be set");
    let port = env::var("PORT").expect("Port value must be set");

    //Attempt to make connection to postgresql server
    let port_u16: u16 = port.trim().parse().expect("Invalid number for port");

    match attempt_pgsql_connection(&database, &user, &password, &host, port_u16) {
        Ok(_client) => {
            println!("Connected!");
        }
        Err(e) => {
            eprintln!("Failed to connect: {}", e);
        }
    }    
}   
