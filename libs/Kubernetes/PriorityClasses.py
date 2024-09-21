from pulumi_kubernetes.meta.v1 import ObjectMetaArgs
from pulumi_kubernetes.scheduling.v1 import PriorityClass

low_priority = PriorityClass(
    "low-priority",
    description="Low PriorityClass",
    global_default=False,
    value=500000,
    preemption_policy="PreemptLowerPriority",
    metadata=ObjectMetaArgs(name="low-priority"),
)

medium_priority = PriorityClass(
    "medium-priority",
    description="Medium PriorityClass",
    global_default=False,
    value=750000,
    preemption_policy="PreemptLowerPriority",
    metadata=ObjectMetaArgs(name="medium-priority"),
)

high_priority = PriorityClass(
    "high-priority",
    description="High PriorityClass",
    global_default=False,
    value=1000000,
    preemption_policy="PreemptLowerPriority",
    metadata=ObjectMetaArgs(name="high-priority"),
)
