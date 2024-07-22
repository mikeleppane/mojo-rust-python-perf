use clap::Parser;
use n_body_rust::simulate;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    #[arg(short, long, default_value = "1000")]
    steps: usize,
}

fn cli() -> Args {
    Args::parse()
}

fn main() {
    let args = cli();
    let n_steps = args.steps;
    simulate(n_steps);
}
