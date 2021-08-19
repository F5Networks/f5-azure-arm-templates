#!/bin/bash
# global env vars
export DEWPT_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEA15ymjD7RpZRpWZclSMadeNb7rA506hZrPIM48xCduSP+rSoc\nJFSjmLKPM0bJP15TLyu+Upqfy5juMqlsnXBv5idcDV7JYtM8q2I2S223Y5ncz65s\nxmF4tObHIpglDQ2fSer/GAeoUXve5boxJDwmfQYBRScFtZcY99Y6YduHI7W2CADr\noI5WmAT18mil7X4KVF9L4D6MYB/Vu+XG2/gKfJv/Uf1dQeCarRHMFLdc1k9/UAPz\nC0uDiSM94ZjD4wpaqTdU+fCeFV3NEp0vyGG3etFW36pfx/5X+x4LLwtpb4AHtVCl\nZcH/LI2n5ShgQgWlgx6Qj73a2i0cTcCqj6Y/UwIBJQKCAQARe2dzJ7AiLqDCEyyJ\nXDZIEW5aDwKPhUb3EY7+84Jo9RSmQa9BN0uI6+IY6hBRPv/TZGlgpMDZKBNQN0Ao\ncOZ6ceTefU6ZT2XItO+lQD9NQ9OiIuY5mTNM8B374tKSWwzqUVL0HEvq7l4uTV3u\nLmP8TJhRtw5M/mnO59s4Xehc1zuqx7AMA2qVvpimpJhWqRejo7PSqIoJ9PK94jg7\n2LZNSxalKtdeBSRluSruHMp9jMgwfg80R7pGOQReNY0OtNyfI11x9aH0r23USUDy\n6ZPVIwuhHgJxBlQNvlcOtR82GMiBTVJAcgYdChBy89I/MHG14qoV0ilco1X9hi9R\noiR9AoGBAPLZNjYOiMbjxugqXhtzQFEZN6qF16Km1pbAeSg5sokkQUdAI7BRu6of\ndkM+KqrtW8oR9mwHgwMsEaeYu/vnUuU/F4VcKCqWh9R6jgjXp9+CTQXfO3F1Q3N+\nD4TWDneAJn31Ak9ZdSQNWnqXH41jId6Nwr72ZRd6bHGcl8IkS+j5AoGBAONJ1o+o\nhhfSughrcd5NbZWuRKI0SEM+fDfVhpPAKg5JvKDHc/dokC+nBSIIfvCHK2WSpXYp\nqTGlp7W+8vxGVim/a6R1naYKYlizMls8zmNefsGSp3rgwi0o4v9OQxupfTYwP1+c\nI+UOYbfESbHTjkyHcEqMOMU+jNt6XKDR3+mrAoGALfG+JecS9TIDCVQfpFQTFkMK\niAt70qnxPx1+tJVLSmDOFGYUlvq0zSiL/uI/bHIYSNL3RN7TmND8a9DJnlwyRwvv\nsXJMyclzpL09d0tk8u8jVCNQb2k2RkhIIAzSTfWmattTdsu8N0DL7a3jX/ApAJdc\nMfdDjtH41zlNJLrCQNUCgYEAn7dYgJ/vhly6E8EflUsqaS5Zvhbmq8sLLidXphhU\n53IV2MOB7B/2ngapqTZnCeJxhaVRrPquPpAU/ED9xgfphR66V+PyPVNns/OLK1sp\nPuh0v2AiqV+rCvoi+JfcIUarA3vZgXSjmgobJy/8bx8KDEN/VvrAG+bD2H9/XEBz\n1KECgYEAxUetgsf/f1/eokoiNqSqYkGsGVqes7W7kCmQ1HutxFabrBgjmlnt7guk\nI0uxYONvN25lPzgy+k4mpH/CvBbD8pvIxSaIgNT39cmVnGUpKfUVFxr/mTWmTTue\n57QvBZL4+93DYQMVcjrjkogcyMweag1t/4SWulbR49Fy8wqKtOs=\n-----END RSA PRIVATE KEY-----
export STACK_TYPE=dewdrop-dev

# Azure
# Azure environmental variables
export AZURE_TENANT_ID=d106871e-7b91-4733-8423-f98586303b68
export AZURE_CLIENT_ID=d40aad56-b0bd-466d-a6c4-6c9c4d0f9aa7
export AZURE_SERVICE_PRINCIPAL=D9T91uX_A_8.v6KNgOX6FD~F2rbU.kB9y_
export AZURE_SUBSCRIPTION_ID=d18b486a-112d-4402-add2-7fb1006f943a

# Modules
export AZURE_TEMPLATE_TEST_URL_STANDALONE=file:///automated-test-scripts/f5-azure-arm-templates/supported/standalone/daily_test.yaml
export AZURE_TEMPLATE_TEST_PARAMS_STANDALONE=/automated-test-scripts/data/f5-azure-arm-templates/supported/standalone/1nic/existing-stack/bigiq/prepub_parameters.yaml

