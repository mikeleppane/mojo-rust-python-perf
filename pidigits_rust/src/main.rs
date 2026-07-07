use clap::Parser;
use color_eyre::eyre::Result;

#[derive(Parser, Debug)]
#[command(version, about = "Compute digits of pi via the Chudnovsky algorithm")]
struct Args {
    /// Number of decimal digits of pi to compute.
    #[arg(short, long, default_value_t = 1000)]
    digits: u32,
}

fn main() -> Result<()> {
    color_eyre::install()?;
    let args = Args::parse();
    let (elapsed_ms, pi) = pidigits_rust::run(args.digits)?;

    // Sanity-check prefix (formatting the full result is excluded from timing).
    let preview = pi.to_string_radix(10, Some(20.min(args.digits as usize).max(2)));
    eprintln!(
        "pi: {} digits in {elapsed_ms:.2} ms (starts {preview})",
        args.digits
    );
    // Machine-readable line consumed by the benchmark harness.
    println!("ELAPSED_MS {elapsed_ms:.3}");
    Ok(())
}
