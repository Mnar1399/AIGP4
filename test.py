import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.identity import DefaultAzureCredential

# إعداد الـ endpoint واسم التوزيع
endpoint = "https://mnar6-m47j94ok-swedencentral.cognitiveservices.azure.com/"
deployment_name = "gpt-35-turbo"

# إنشاء عميل باستخدام الـ endpoint واسم التوزيع
client = ChatCompletionsClient(
    endpoint=endpoint,
    deployment_name=deployment_name,  # اسم التوزيع هنا عند تهيئة العميل
    credential=DefaultAzureCredential(),
)

# استدعاء الدالة للحصول على رد
response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="I am going to Paris, what should I see?"),
    ],
    temperature=1.0,
    top_p=1.0,
    max_tokens=1000,
)

# طباعة النتيجة
print(response.choices[0].message.content)
