# --- 2. LOGOTIPO Y ENCABEZADO COMERCIAL DE ALTO IMPACTO ---
st.markdown("""
    <div style="display: flex; align-items: center; background: linear-gradient(135deg, #0f172a 0%, #064e3b 55%, #059669 100%); padding: 28px 32px; border-radius: 22px; box-shadow: 0 25px 40px -12px rgba(6,78,59,0.35); margin-bottom: 24px; color: white; flex-wrap: wrap; gap: 20px; border: 1px solid rgba(16, 185, 129, 0.2);">
        <div style="flex-shrink: 0; background: rgba(255, 255, 255, 0.08); padding: 10px; border-radius: 18px; backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center;">
            <svg width="56" height="56" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="eliteGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#10B981" />
                  <stop offset="100%" stop-color="#059669" />
                </linearGradient>
                <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#FBBF24" />
                  <stop offset="100%" stop-color="#D97706" />
                </linearGradient>
              </defs>
              <path d="M32 4L56 16V48L32 60L8 48V16L32 4Z" fill="url(#eliteGrad)" fill-opacity="0.18" stroke="url(#eliteGrad)" stroke-width="2"/>
              <path d="M16 26C20 20 26 18 32 22C38 18 44 20 48 26" stroke="url(#goldGrad)" stroke-width="3.5" stroke-linecap="round"/>
              <circle cx="32" cy="22" r="3.5" fill="#FBBF24"/>
              <circle cx="32" cy="38" r="7" fill="url(#eliteGrad)" stroke="#FFFFFF" stroke-width="2"/>
              <path d="M32 25V31" stroke="url(#goldGrad)" stroke-width="2.5" stroke-linecap="round"/>
              <path d="M25 38H20M39 38H44" stroke="url(#eliteGrad)" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
        <div style="flex-grow: 1; min-width: 240px;">
            <h1 style="margin: 0; font-size: 2.05em; color: #ffffff; letter-spacing: -0.8px; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800;">
                Ganader-IA <span style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #0f172a; padding: 2px 10px; border-radius: 8px; font-size: 0.52em; vertical-align: middle; font-weight: 800; letter-spacing: 0.8px; box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);">ELITE 360</span>
            </h1>
            <p style="margin: 6px 0 0 0; font-size: 0.94em; color: #cbd5e1; font-weight: 400; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.2px;">
                Plataforma SaaS de Precisión Nutricional, Economía y Sostenibilidad Pecuaria
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)
