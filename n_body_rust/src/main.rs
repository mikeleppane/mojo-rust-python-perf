use clap::Parser;

#[derive(Parser, Debug)]
#[command(version, about = "N-body simulation of the outer solar system")]
struct Args {
    /// Number of integration steps to run.
    #[arg(short, long, default_value_t = 1000)]
    steps: usize,
}

fn main() {
    let args = Args::parse();
    let (elapsed_ms, conserved) = n_body_rust::run(args.steps);

    if !conserved {
        eprintln!("warning: energy was not conserved");
    }
    eprintln!("N-body: {} steps in {elapsed_ms:.2} ms", args.steps);
    // Machine-readable lines consumed by the benchmark harness.
    println!("ELAPSED_MS {elapsed_ms:.3}");
    println!("CONSERVED {conserved}");
}
