# Paired effect estimates

구조 점수는 결함이 확인된 두 리뷰 픽스처를 제외하고 PRD 생성+화면정의만 사용한다. Judge 점수는 18개 bundle에서 두 judge 평균을 cluster로 사용한다.

| Contrast | Structural Δpp [95% bootstrap CI] | Blind quality Δ/100 [95% bootstrap CI] |
|---|---:|---:|
| model generation: `M56-CURRENT` − `M55-CURRENT` | +4.8 [-5.8, +18.3] | +6.0 [-1.2, +12.2] |
| current harness: `M56-CURRENT` − `M56-BARE` | +16.3 [+9.6, +24.0] | +3.1 [-1.5, +7.1] |
| redesign: `M56-OPT` − `M56-CURRENT` | +17.3 [+8.7, +25.0] | +1.0 [-2.6, +4.7] |
| optimized net: `M56-OPT` − `M56-BARE` | +33.7 [+21.2, +45.2] | +4.0 [-0.7, +8.5] |
