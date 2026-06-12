import streamlit as st
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials
import base64, json, datetime

# ─── CONFIGURAÇÕES ───────────────────────────────────────
GROQ_KEY    = "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"
PLANILHA_ID = "1rBaBnwQfxwGZK--R7gSdhxs1qo4CyVFwIVlZH-m6QRs"

cred_dict = {
  "type": "service_account",
  "project_id": "gen-lang-client-0256898745",
  "private_key_id": "68776c576763974209af31c17f44bba00e0590bd",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDFYKDb9egyiBbO\noNeqFy6ulz950ZvsGs8Hr8+LPJreTcAsAei9CX7gPK+tDG9hhIRGunYr4sBqq7+J\nHaTiBzbBSp7t1U32ULEe0BYLr9juNgREBhmCWLGytwEdR6YLSIUg/nXeqpjAKUKk\n41c72PnvlVngvh8UgD0ejh1OcvSuMul/nStVrWb4Vi1B/bf8QGA2ZZBvPP0bzbox\nQeeyPcJQOsxBy2pFAorvnq4io7LUl1Q1SfO8+k9OwvZRMjzu5JjJGTXR7fWtS59p\nycWxPoj8gzm2DerpLHBjzrjVdk+qbB72B9dVbc/dE0b6DUyubGHKoXn09Sl01V0s\npvVQQDuDAgMBAAECggEALDAF0ziqUyXEdV3s6ldmTA/wVgVnMuSNlNr3S+S1hy9A\n5plG0YterDTp34P5K4vPUUZNTmXlTfxFVR0d3LxgtcVO70/htFM8U/mh9dvYZPwS\n2GfFLjlNDwWJalSwB7akl05gdQkcSWjzUpbS4MMisVBuXrIxoxVSmZSXWwjBXn4C\nftYKQqwcSDEbINmlmX/JF6Pqh/wd+FJR6thnRM2LxUM3AGg7N6+/FMnhIM/FY5Mk\n8E6N9FgxFspjF+cqTNbyIPAq1ev8pFacpVibQdLApt0SduwYPbqIStF4d5oTZ5wT\nsn6CqZKytweI7EqkZpUgZ7oPvFVjXlAXjS3gxhtxAQKBgQDxpwYEcoGeXV50OJYF\nHk7zFGHPpKpp7a+J9Qj5A8E+hY/HkrIncDmx9Dm+gE0eQ53CIk2uG22AP5DiLk2i\n3+YSXR/Lpzr3+43Qpn3p2QklLaEcI+lJbStMxp06433ZW6LpZ0wnyl5ktKarr1ZQ\nUkG3uRTPvtkcg4ZO2zDaWhxsyQKBgQDRGKagdDqZEjgnRnXS6rDkfROgwhTYDth/\nAs/tVaA9HMMXmruJLwtzkFC7hZFglQN443cjPg7OzEYBq8l71pR1QTiUxhQZDCLZ\nuJiezaKArJW9L+Zj5TQfVUam0zekV3MG9fzr+3kClAFn24rdWcRdoWtQNOdK2qK0\neQJI9Ifn6wKBgFQvGpKMDYnM/y2/1Mt9roVSMWzz8YYrjn6iBXkyjKyqPNeKzFOe\n7gqHiWJLMhJ7/cZ2ytb/qRsHigKxnMxD8dOt63i4Dnv7f4ETr0O7H0t7ZOf3vrqc\ntHvvqTCttdb17IAhQ0+NWWr94B5pW8lpjolhidWBqAMd8rkf9RnsUIC5AoGAWIOl\n7eCl+ayDxuSF9i5RibgE+hWOu1O1hDbNjHul5JjrYW+oGc+nellKQ8esHgWWvbMU\n+P9JR3Oj4ws0tM7Gc8iTSi97zIqdqisBuJ/2PaBRlw/S6NDbOrRfvzlEobY/RGAX\nnFINDPFYkv2WEFPy02wEwKRUkRRyshFTzUxux9cCgYAmN10mNUygVQH/KUc7aFzh\nav8HTF//8FVPTJTSwkWvuFysByzwiUJ34CXoF5qYkKTjbnc2On3VVzqhyxOszskc\nxzFcVwq1r/MVNiIxwJkmD/dOoo15/Rg01R1EyiwMMXFI2tGVQFdtsxNdhFid9u/n\nnY2WnWsEeroz3AoyaI4m9w==\n-----END PRIVATE KEY-----\n",
  "client_email": "bot-nf@gen-lang-client-0256898745.iam.gserviceaccount.com",
  "client_id": "101838153435326324441",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bot-nf%40gen-lang-client-0256898745.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
# ─────────────────────────────────────────────────────────

st.title("📋 Leitor de Nota Fiscal")

@st.cache_resource
def conectar_planilha():
    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(cred_dict, scopes=scopes)
    gc = gspread.authorize(creds)
    planilha = gc.open_by_key(PLANILHA_ID).sheet1
    if planilha.cell(1, 1).value is None:
        planilha.append_row(["Data processamento", "Estabelecimento", "Data NF",
                             "Descrição", "Qtd", "Valor unitário", "Valor total", "Total NF"])
    return planilha

foto = st.camera_input("📷 Tirar foto da nota") or st.file_uploader(
    "ou fazer upload", type=["jpg", "jpeg", "png", "webp"])

if foto:
    st.image(foto, caption="Nota fiscal", use_column_width=True)

    if st.button("🔍 Processar nota fiscal"):
        with st.spinner("Analisando..."):
            dados = base64.standard_b64encode(foto.read()).decode("utf-8")
            media_type = "image/jpeg" if foto.name.endswith((".jpg",".jpeg")) else \
                         "image/png" if foto.name.endswith(".png") else "image/webp"

            client = Groq(api_key=GROQ_KEY)
            resposta = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{dados}"}},
                        {"type": "text", "text": 'Extraia os itens desta nota fiscal. Responda SOMENTE em JSON: {"estabelecimento":"","data":"","itens":[{"descricao":"","qtd":1,"valor_unit":0.00,"valor_total":0.00}],"total":0.00}'}
                    ]
                }],
                max_tokens=1024
            )

            texto = resposta.choices[0].message.content.strip().removeprefix("```json").removesuffix("```").strip()
            nf = json.loads(texto)

        st.success(f"✓ {len(nf['itens'])} itens encontrados")
        st.subheader(f"🏪 {nf.get('estabelecimento','')}")
        st.caption(f"Data: {nf.get('data','')}")

        for item in nf["itens"]:
            st.write(f"• {item['descricao']} — {item['qtd']}x R$ {item['valor_unit']:.2f} = **R$ {item['valor_total']:.2f}**")

        st.metric("Total", f"R$ {nf.get('total', 0):.2f}")

        if st.button("💾 Salvar na planilha"):
            planilha = conectar_planilha()
            agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            for item in nf["itens"]:
                planilha.append_row([
                    agora,
                    nf.get("estabelecimento", ""),
                    nf.get("data", ""),
                    item.get("descricao", ""),
                    item.get("qtd", 1),
                    item.get("valor_unit", 0.0),
                    item.get("valor_total", 0.0),
                    nf.get("total", 0.0)
                ])
            st.success("✓ Salvo na planilha!")
