use std::hint::black_box;

use criterion::{Criterion, criterion_group, criterion_main};
use pidigits_rust::chudnovsky;

fn pidigits_benchmark(c: &mut Criterion) {
    let mut group = c.benchmark_group("pidigits");
    // Big-integer work is slow; keep the sample count modest.
    group.sample_size(10);

    for digits in [1_000_u32, 10_000, 100_000] {
        group.bench_function(format!("{digits} digits"), |b| {
            b.iter(|| {
                let pi = chudnovsky(black_box(digits)).expect("valid digit count");
                black_box(pi);
            });
        });
    }

    group.finish();
}

criterion_group!(benches, pidigits_benchmark);
criterion_main!(benches);
