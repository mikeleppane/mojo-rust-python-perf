use std::hint::black_box;

use criterion::{BatchSize, Criterion, criterion_group, criterion_main};
use n_body_rust::{advance, create_initial_system, energy, offset_momentum};

fn n_body_benchmark(c: &mut Criterion) {
    let mut group = c.benchmark_group("n-body");

    for steps in [10_000_usize, 100_000, 1_000_000] {
        group.bench_function(format!("{steps} steps"), |b| {
            b.iter_batched(
                || {
                    // Fresh, momentum-corrected system for every sample so state
                    // does not accumulate across iterations.
                    let mut system = create_initial_system();
                    offset_momentum(&mut system);
                    system
                },
                |mut system| {
                    for _ in 0..steps {
                        advance(&mut system);
                    }
                    black_box(energy(&system));
                },
                BatchSize::SmallInput,
            );
        });
    }

    group.finish();
}

criterion_group!(benches, n_body_benchmark);
criterion_main!(benches);
