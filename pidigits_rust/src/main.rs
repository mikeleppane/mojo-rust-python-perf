use clap::Parser;
use pidigits_rust::chudnovsky;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    #[arg(short, long, default_value = "1000")]
    digits: u32,
}

fn cli() -> Args {
    Args::parse()
}

fn main() {
    let args = cli();
    let digits = args.digits;
    let pi = chudnovsky(digits).expect("Failed to calculate pi");
    println!("{pi}");
}
