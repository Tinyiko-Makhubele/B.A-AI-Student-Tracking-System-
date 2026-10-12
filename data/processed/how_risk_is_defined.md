# How risk is defined

This note summarises the prediction rules for the OULAD dataset. Preparation details and data checks are in [data_quality_notes.md](data_quality_notes.md), and column descriptions are in [dataset_guide.md](dataset_guide.md).

- **Prediction unit:** one student in one module presentation.
- **Checkpoint:** day 63. Include only students still registered on that day and use activity recorded by the end of day 63.
- **At risk (1):** final result is Fail or Withdrawn.
- **Not at risk (0):** final result is Pass or Distinction.

Use course context, prior study information, assessment submissions due by day 63, and VLE activity through day 63 as candidate inputs. Keep demographic fields for subgroup checks only; use student ID only to group records and make the evaluation split.

Exclude final results and the risk label from model inputs. Also exclude post-checkpoint activity, assessments due after day 63, unregistration date as a predictor, and assessment scores because their availability time is unknown.

The prepared table contains 26,292 eligible student-course records. No model has been trained.
