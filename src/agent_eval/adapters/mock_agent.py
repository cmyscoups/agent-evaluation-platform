
from copy import deepcopy

from agent_eval.adapters.base import AgentAdapter
from agent_eval.models.test_case import TestCase
from agent_eval.models.agent_result import AgentResult, ToolCall
from agent_eval.collectors.trace_collector import TraceCollector


class MockAgentAdapter(AgentAdapter):

    def __init__(self, collector: TraceCollector):
        self.collector = collector

    def run(self, test_case: TestCase) -> AgentResult:
        return self._execute(test_case)
    
    def _execute(self, test_case: TestCase) -> AgentResult:
        fixtures = deepcopy(test_case.fixtures)
        tool_failures = test_case.mock_config.get("tool_failures", [])
        

        conversation = test_case.input.get("conversation", [])
        user_message = conversation[-1]["content"]

        if "退款" in user_message:
            intent = "refund"
        else:
            intent = "unknown"

        tool_calls = []
        final_state = {}

        if intent == "refund":
            order = fixtures["orders"][0]
            order_id = order["order_id"]

            # 查询订单
            self.collector.start_span(
                "query_order",
                attributes={"order_id": order_id},
            )
            self.collector.add_event(
                "tool_call",
                attributes={"tool_name": "query_order",
                "status": "success",},
            )

            tool_calls.append(
                ToolCall(
                    name="query_order",
                    arguments={"order_id": order_id},
                )
            )

 
            self.collector.end_span(status="success")

            # 执行退款
            if (
                order["fulfillment_status"] == "unshipped"
                and order["refund_status"] == "none"
            ):
                self.collector.start_span(
                    "refund_order",
                    attributes={"order_id": order_id},
                )
                if "refund_order" in tool_failures:
                    status = "failed"
                    response = "退款失败"
                else:
                    status = "success"
                    response = "退款成功"
                    order["refund_status"] = "refunded"

                self.collector.add_event(
                    "tool_call",
                    attributes={
                        "tool_name": "refund_order",
                        "status": status,
                    },
                )

                tool_calls.append(
                    ToolCall(
                        name="refund_order",
                        arguments={"order_id": order_id},
                        status=status,
                    )
                )

                self.collector.end_span(status=status)

            else:
                response = "当前订单不满足退款条件"

            final_state = {
                "order_id": order_id,
                "refund_status": order["refund_status"],
            }

        else:
            response = "暂时无法识别您的需求"

        return AgentResult(
            response=response,
            intent=intent,
            tool_calls=tool_calls,
            final_state=final_state,
        )
