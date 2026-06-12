import streamlit as st
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials
import base64, json, datetime

st.title("📋 Leitor de Nota Fiscal")

@st.cache_resource
def conectar_planilha():
    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes)
    gc = gspread.authorize(creds)
    planilha = gc.open_by_key(st.secrets["PLANILHA_ID"]).sheet1
    if planilha.cell(1, 1).value is None:
        planilha.append_row(["Data processamento", "Estabelecimento", "Data NF",
                             "Descrição", "Qtd", "Valor unitário", "Valor total", "Total NF"])
    return planilha

foto = st.camera_input("📷 Tirar foto da nota") or st.file_uploader(
    "ou fazer upload", type=["jpg", "jpeg", "png", "webp"])

if foto:
    st.image(foto, caption="Nota fiscal", use_column_width=True)

    if st.button("🔍 Processar nota fiscal"):
        foto.seek(0)
        dados = base64.standard_b64encode(foto.read()).decode("utf-8")
        ext = foto.name.split(".")[-1].lower() if hasattr(foto, "name") else "jpg"
        media_types = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                       "png": "image/png", "webp": "image/webp"}
        media_type = media_types.get(ext, "image/jpeg")

        with st.spinner("Analisando..."):
            client = Groq(api_key=st.secrets["GROQ_KEY"])
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
        st.session_state["nf"] = nf
        st.session_state["processado"] = True

if st.session_state.get("processado"):
    nf = st.session_state["nf"]
    st.success(f"✓ {len(nf['itens'])} itens encontrados")
    st.subheader(f"🏪 {nf.get('estabelecimento','')}")
    st.caption(f"Data: {nf.get('data','')}")
    for item in nf["itens"]:
        st.write(f"• {item['descricao']} — {item['qtd']}x R$ {item['valor_unit']:.2f} = **R$ {item['valor_total']:.2f}**")
    st.metric("Total", f"R$ {nf.get('total', 0):.2f}")

    if st.button("💾 Salvar na planilha"):
        with st.spinner("Salvando..."):
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
        st.session_state["processado"] = False
