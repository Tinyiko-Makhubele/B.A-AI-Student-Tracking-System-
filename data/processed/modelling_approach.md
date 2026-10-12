# How we plan to use this dataset

## What the dataset covers

This is an early research exercise using historical data from the Open University Learning Analytics Dataset (OULAD). It covers seven modules across 22 course presentations, with one row for each student in each presentation.

Because this is public data from another institution, it can help us explore the approach, but it can’t tell us how students at our institution are doing.

## What we want to predict

The first task is to sort records into two groups using the `at_risk` label:

- `1`: the student’s final result was Fail or Withdrawn
- `0`: the final result was Pass or Distinction

The proposed prediction point is course day 63. The features are based on course details, prior study, assessments due and submitted by that point, and VLE activity recorded up to that day.

Final results are used to create the label, not as model inputs. Student IDs were used to group records and prepare the evaluation split, then removed from the shared dataset. Demographic details remain available for subgroup checks, but should not be used as model inputs. The cutoff and split columns describe the data; they are not predictors.

No model has been trained yet.

## How we’ll judge a future model

About 41.5% of the records are labelled at risk, so accuracy on its own may not tell the whole story. When we build a baseline, we should look at which at-risk students it misses and how many students it flags unnecessarily. The confusion matrix, precision, recall, and F1 score can help show that balance. A precision-recall view can also help when comparing alert thresholds.

Missing a student who could benefit from support is a concern. So is sending too many unnecessary alerts when staff time is limited. The threshold should be considered with both of these effects in mind.

For the initial evaluation, presentation 2014J is held aside. Earlier records for students who also appear in that presentation are excluded from training, so the same student does not appear in both groups.

## The lecturer’s role

A risk indication should be a prompt to take a closer look, not a conclusion about a student. A lecturer or advisor can consider the wider context and decide whether reaching out would be helpful. Any decision about grades, progression, services, or support stays with the people responsible for the student.
