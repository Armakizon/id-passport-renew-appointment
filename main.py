# main.py

from access_govisit import get_govisit_token
from govisit_requests import APIcall

token = get_govisit_token(wait_for_code=60)
#token= 'eyJhbGciOiJBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwidHlwIjoiSldUIiwiY3R5IjoiSldUIn0.lnpndjJ1QJrhSoLSSjE2J8JXj18JK-dTyZ3XrsTb0JSxYBjF9qc2iw.RVu24tCewvIBhr-aEBWWew.yEKrz1vMEn9BcjqB8QPDAcD3M93oRbuPp7s11tsAiyvdAtWW2L6Jv-3HxgJVujLrjcyalWv8IrNjSm_o5h0OV4m_jfUSeNV4fclAdyCnhy9mB6c8r4N4gj5RcAgvBkn9kE26K_muqb7ut4q2wxeN2fJG8Dc8_6FWtbKVij29xbVA4EYfSJWPoVLh0ZGk_TUesyx51NTGRTzXvoxwk1oWSJN60Z8yumviCua1DVi6ccyo0qQbGnznzeZ_wS1o-2ojZLxdGeXdTMEcQORIy72yCQuryQiR4VosdiznQzZEzQUHicWTy-8hc4d9zAY5eLgnOKMRNlyb6qOgvE1p61RSLAyG9PYRhZbj6fuz622nsaUvaDwLbZvTPHyYVIQu-CbD.2TRNXVouqD_izvBXii-r8A'

if token:
    print("🎉 Token received:")
    print(token)
    APIcall(token)  # Default CSV is "branch_ids.csv"
else:
    print("⚠️ Failed to retrieve token.")
