use criterion::{black_box, criterion_group, criterion_main, Criterion};
use pidigits_rust::chudnovsky;

pub fn pidigits_benchmark(c: &mut Criterion) {
    let mut group =
        c.benchmark_group("Pi Digits Calculation with 1_000, 10_000, 100_000, 1_000_000 digits");

    group.bench_function("1_000 steps", |b| {
        b.iter(|| {
            let pi = chudnovsky(1_000).expect("Failed to calculate pi");
            black_box(pi);
        });
    });

    group.bench_function("10_000 steps", |b| {
        b.iter(|| {
            let pi = chudnovsky(10_000).expect("Failed to calculate pi");
            black_box(pi);
        });
    });

    group.bench_function("100_000 steps", |b| {
        b.iter(|| {
            let pi = chudnovsky(100_000).expect("Failed to calculate pi");
            black_box(pi);
        });
    });

    group.bench_function("1_000_000 steps", |b| {
        b.iter(|| {
            let pi = chudnovsky(1_000_000).expect("Failed to calculate pi");
            black_box(pi);
        });
    });

    group.finish();
}

criterion_group!(benches, pidigits_benchmark);

criterion_main!(benches);
