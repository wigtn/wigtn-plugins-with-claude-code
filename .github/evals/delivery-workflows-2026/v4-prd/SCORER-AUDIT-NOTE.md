# v4 PRD scorer audit note

During the 51 model calls, a static review incorrectly concluded that the
frozen scorer's repository-root expression should use `root.parents[2]`
instead of `root.parents[3]`. Execution disproved that conclusion:
`root` is the `v4-prd` directory itself, so `parents[3]` is the repository and
`parents[2]` is `.github`.

The attempted change caused aggregation to fail before any score was produced.
The scorer was restored byte-for-byte to the manifest-pinned original and then
rerun. No model call, fixture, generated output, grading rule, or final score
was affected.
