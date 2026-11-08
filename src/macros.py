"""Synthetic approved macros and tone snippets for Tamara CX (hackathon only)."""

from __future__ import annotations

from typing import Any

ISSUE_TYPES: dict[str, str] = {
    "refund_arn": "Refund ARN",
    "unrecognized_charge": "Unrecognized charge",
    "evidence_request": "Evidence request",
}

# Approved-style phrasing only — synthetic, not real Tamara KB content.
MACROS: dict[str, dict[str, Any]] = {
    "refund_arn": {
        "label": "Refund ARN",
        "required_hints": ["order_id"],
        "tone_en": (
            "Empathetic, clear, and professional. Confirm the refund request, "
            "reference the order ID when available, and explain that the ARN "
            "(Acquirer Reference Number) will be shared so the customer can "
            "follow up with their bank if needed. Do not invent bank timelines."
        ),
        "tone_ar": (
            "نبرة متعاطفة وواضحة ومهنية. أكّد طلب الاسترداد، واذكر رقم الطلب "
            "إن وُجد، واشرح أن رقم ARN سيُشارك لمتابعة البنك عند الحاجة. "
            "لا تخترع مواعيد بنكية."
        ),
        "template_en": (
            "Dear Customer,\n\n"
            "Thank you for contacting Tamara Care.\n\n"
            "We have processed your refund request for order {order_id}. "
            "Your Acquirer Reference Number (ARN) is {arn}. "
            "Please share this ARN with your bank if the refund has not "
            "appeared on your statement yet. Bank posting times may vary.\n\n"
            "If you need anything else, we are here to help.\n\n"
            "Kind regards,\n"
            "Tamara Care Team"
        ),
        "template_ar": (
            "عزيزي العميل،\n\n"
            "شكرًا لتواصلك مع رعاية تمارا.\n\n"
            "تمت معالجة طلب الاسترداد الخاص بطلبك رقم {order_id}. "
            "رقم المرجع لدى البنك (ARN) هو {arn}. "
            "يرجى مشاركة هذا الرقم مع بنكك إذا لم يظهر المبلغ في كشف حسابك بعد. "
            "قد تختلف أوقات ظهور العملية حسب البنك.\n\n"
            "إذا احتجت أي مساعدة إضافية، نحن هنا لخدمتك.\n\n"
            "مع أطيب التحيات،\n"
            "فريق رعاية تمارا"
        ),
        "case_issue_template": (
            "Customer requested refund ARN for order {order_id}."
        ),
        "case_solution_template": (
            "Confirmed refund processing and shared ARN {arn} with the customer "
            "via email. Advised bank posting times may vary."
        ),
        "defaults": {
            "order_id": "TMP-00000",
            "payment_id": "PAY-00000",
            "arn": "ARN-SYNTH-000000",
        },
    },
    "unrecognized_charge": {
        "label": "Unrecognized charge",
        "required_hints": ["order_id", "payment_id"],
        "tone_en": (
            "Calm and reassuring. Acknowledge the concern about an unrecognized "
            "charge, reference order/payment IDs when available, summarize what "
            "was verified, and outline the next step clearly. Never accuse the "
            "customer of fraud."
        ),
        "tone_ar": (
            "نبرة هادئة ومطمئنة. اعترف بقلق العميل بشأن عملية غير معروفة، "
            "واذكر أرقام الطلب/الدفع إن وُجدت، ولخّص ما تم التحقق منه، "
            "وحدّد الخطوة التالية بوضوح. لا تتهم العميل بالاحتيال."
        ),
        "template_en": (
            "Dear Customer,\n\n"
            "Thank you for contacting Tamara Care.\n\n"
            "We reviewed the charge linked to order {order_id} "
            "(payment {payment_id}). Based on our checks, this payment is "
            "associated with your Tamara purchase. If this still does not look "
            "familiar, reply with any extra details and we will continue the "
            "investigation.\n\n"
            "Kind regards,\n"
            "Tamara Care Team"
        ),
        "template_ar": (
            "عزيزي العميل،\n\n"
            "شكرًا لتواصلك مع رعاية تمارا.\n\n"
            "راجعنا العملية المرتبطة بالطلب رقم {order_id} "
            "(الدفع {payment_id}). وفق التحقق لدينا، ترتبط هذه العملية "
            "بشراء عبر تمارا. إذا بقيت غير مألوفة لديك، أرسل أي تفاصيل إضافية "
            "وسنواصل التحقق.\n\n"
            "مع أطيب التحيات،\n"
            "فريق رعاية تمارا"
        ),
        "case_issue_template": (
            "Customer reported an unrecognized charge on order {order_id} "
            "/ payment {payment_id}."
        ),
        "case_solution_template": (
            "Verified payment linkage to the Tamara order and explained findings "
            "to the customer. Offered to continue investigation if still unclear."
        ),
        "defaults": {
            "order_id": "TMP-00000",
            "payment_id": "PAY-00000",
            "arn": "ARN-SYNTH-000000",
        },
    },
    "evidence_request": {
        "label": "Evidence request",
        "required_hints": ["order_id"],
        "tone_en": (
            "Helpful and precise. Clearly list the documents or screenshots "
            "needed, explain why they are required, and set a polite expectation "
            "for next steps after evidence is received."
        ),
        "tone_ar": (
            "نبرة مفيدة ودقيقة. اذكر بوضوح المستندات أو لقطات الشاشة المطلوبة، "
            "واشرح سبب الحاجة إليها، وحدّد بأدب الخطوة التالية بعد الاستلام."
        ),
        "template_en": (
            "Dear Customer,\n\n"
            "Thank you for contacting Tamara Care.\n\n"
            "To continue reviewing order {order_id}, please reply with the "
            "following evidence:\n"
            "1) A clear screenshot of the transaction or bank statement line\n"
            "2) Any merchant confirmation or delivery proof you have\n\n"
            "Once we receive these, we will continue the review and update you.\n\n"
            "Kind regards,\n"
            "Tamara Care Team"
        ),
        "template_ar": (
            "عزيزي العميل،\n\n"
            "شكرًا لتواصلك مع رعاية تمارا.\n\n"
            "لمتابعة مراجعة الطلب رقم {order_id}، يرجى الرد بالمستندات التالية:\n"
            "1) لقطة شاشة واضحة للعملية أو سطر كشف الحساب البنكي\n"
            "2) أي تأكيد من التاجر أو إثبات تسليم متوفر لديك\n\n"
            "بعد الاستلام سنكمل المراجعة ونوافيك بالتحديث.\n\n"
            "مع أطيب التحيات،\n"
            "فريق رعاية تمارا"
        ),
        "case_issue_template": (
            "Additional evidence required from customer for order {order_id}."
        ),
        "case_solution_template": (
            "Requested transaction screenshot and merchant/delivery proof via "
            "email. Awaiting customer response to continue review."
        ),
        "defaults": {
            "order_id": "TMP-00000",
            "payment_id": "PAY-00000",
            "arn": "ARN-SYNTH-000000",
        },
    },
}


def get_macro(issue_type: str) -> dict[str, Any]:
    if issue_type not in MACROS:
        raise KeyError(f"Unknown issue type: {issue_type}")
    return MACROS[issue_type]


def issue_type_options() -> list[tuple[str, str]]:
    return [(key, value["label"]) for key, value in MACROS.items()]
