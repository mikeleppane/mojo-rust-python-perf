use criterion::{black_box, criterion_group, criterion_main, Criterion};
use n_body_rust::{advance, create_initial_system, energy, offset_momentum};

pub fn n_body_benchmark(c: &mut Criterion) {
    let mut group =
        c.benchmark_group("N-Body Simulation with 10_000, 100_000, 1_000_000, 10_000_000 steps");

    let mut initial_system = create_initial_system();

    group.bench_function("10_000 steps", |b| {
        b.iter(|| {
            offset_momentum(&mut initial_system);
            black_box(energy(&initial_system));
            for _ in 0..10_000 {
                advance(&mut initial_system);
            }
            black_box(energy(&initial_system));
        });
    });

    group.bench_function("100_000 steps", |b| {
        b.iter(|| {
            offset_momentum(&mut initial_system);
            black_box(energy(&initial_system));
            for _ in 0..100_000 {
                advance(&mut initial_system);
            }
            black_box(energy(&initial_system));
        });
    });

    group.bench_function("1_000_000 steps", |b| {
        b.iter(|| {
            offset_momentum(&mut initial_system);
            black_box(energy(&initial_system));
            for _ in 0..1_000_000 {
                advance(&mut initial_system);
            }
            black_box(energy(&initial_system));
        });
    });

    group.bench_function("10_000_000 steps", |b| {
        b.iter(|| {
            offset_momentum(&mut initial_system);
            black_box(energy(&initial_system));
            for _ in 0..10_000_000 {
                advance(&mut initial_system);
            }
            black_box(energy(&initial_system));
        });
    });

    group.finish();
}

criterion_group!(benches, n_body_benchmark);

criterion_main!(benches);
