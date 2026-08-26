# Executive Summary

This project analyzes 180,519 supply-chain records to evaluate delivery reliability, late-delivery risk, shipping-mode efficiency, regional delay concentration, and customer-segment exposure.

The analysis finds that only 45.17% of records are free from late-delivery risk, while 54.83% are flagged for late risk. The average actual-versus-scheduled shipping gap is 0.57 days, and positive-delay orders average 1.62 days beyond schedule.

Shipping performance varies sharply by mode. Standard Class performs best, with approximately 61.93% SLA compliance and the lowest late-risk ratio at 38.07%. First Class performs worst, with a 95.32% late-risk ratio and only 4.68% SLA compliance. Second Class also requires attention, with a 76.63% late-risk ratio and an average delivery gap of 1.99 days.

Regional delay risk is broadly distributed rather than confined to one geography, which supports the need for region-level monitoring instead of a single global average. Customer-segment risk is relatively similar across Consumer, Corporate, and Home Office customers, meaning logistics improvement should focus primarily on shipping-mode and regional process issues rather than treating one segment as the sole cause.

Recommended actions are to review SLA design and operational execution for First Class and Second Class, establish automated delay-risk alerts, maintain regional scorecards, use higher-performing shipping patterns as benchmarks, and route operationally critical orders through modes with more reliable SLA compliance when feasible.

A limitation of the supplied dataset is that it contains no order or shipping date column. Therefore, time-based trend analysis and date-range filtering cannot be performed without a dated version of the source data.
