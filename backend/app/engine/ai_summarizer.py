"""
Module 5 — AI Tactical Summarization.

Integrates with NVIDIA NIM API (Llama 3.1 70B) to generate tactical summaries.
Enforces strict AI rules:
- Explain uncertainty
- Avoid hallucinating player identities
- Act as an assistant, not absolute truth
"""
import logging
from typing import Dict, Any, List
import httpx

from ..config import settings
from ..models.engine_event import EngineEvent
from ..models.match_segment import MatchSegment

logger = logging.getLogger(__name__)

# Enforced context for all prompts
SYSTEM_PROMPT = f"""
Sen bir futbol taktik analiz asistanısın. Görevin bir insan analiste yardımcı olmaktır.
Aşağıdaki KURALLARA KESİNLİKLE UYMALISIN:
1. Sen bir asistansın, kesin doğruyu söyleyen bir otorite değilsin.
2. Verilen veri bir bilgisayarlı görü (AI) sisteminden gelir ve hatalar içerebilir. Her zaman belirsizliği ifade et (örn. "görünüyor", "olabilir", "tespit edilmiş").
3. Asla oyuncu isimleri veya spesifik forma numaraları uydurma (veride yoksa).
4. Veride olmayan taktiksel kalıpları (örneğin "tiki-taka", "gegenpressing") uydurma.
5. Sadece sana verilen verilere dayanarak kısa, net ve profesyonel bir analiz yaz.
6. Yanıtının sonuna şu uyarıyı mutlaka ekle: '{settings.AI_DISCLAIMER}'
"""


async def generate_segment_summary(
    segment: MatchSegment,
    events: List[EngineEvent],
) -> str:
    """Generate a tactical summary for a specific match segment."""
    if not events:
        return f"Bu zaman aralığında ({segment.segment_label}) belirgin bir taktiksel olay tespit edilmedi."

    # Prepare data for prompt
    event_summaries = []
    for e in events:
        event_summaries.append(
            f"- {e.timestamp_seconds//60:.0f}. dk: {e.event_type} (Güven: %{int(e.confidence*100)}) - {e.description}"
        )

    events_text = "\n".join(event_summaries)

    prompt = f"""
Aşağıda {segment.segment_label} dakikaları arasındaki maç bölümü için tespit edilen olaylar verilmiştir:

Olay Yoğunluğu: {segment.event_density:.1f} olay/dk
Tehlikeli Atak: {segment.dangerous_attacks}
Hızlı Geçiş: {segment.transition_count}
Ceza Sahası Girişi: {segment.box_entries}

Detaylı Olaylar:
{events_text}

Lütfen bu verileri kullanarak, bu bölümün taktiksel bir özetini (en fazla 3-4 cümle) yaz. 
Hangi takımın daha baskın göründüğünü (veriye dayanarak) ve temel eğilimleri belirt.
"""

    return await _call_nvidia(prompt)


async def generate_match_tactical_draft(
    segments: List[MatchSegment],
    team_name: str,
    opponent_name: str,
) -> str:
    """Generate a high-level tactical draft for the entire match."""
    if not segments:
        return "Maç verisi bulunamadı."

    # Aggregate data
    total_dangerous = sum(s.dangerous_attacks for s in segments)
    total_transitions = sum(s.transition_count for s in segments)
    total_box = sum(s.box_entries for s in segments)

    segment_trends = []
    for s in segments:
        if s.dangerous_attacks > 0 or s.transition_count > 0:
            segment_trends.append(
                f"- {s.segment_label}: {s.dangerous_attacks} tehlikeli atak, {s.transition_count} hızlı geçiş"
            )

    trends_text = "\n".join(segment_trends) if segment_trends else "Belirgin eğilim tespit edilmedi."

    prompt = f"""
{team_name} ve {opponent_name} arasındaki maç için genel bir taktiksel analiz taslağı oluştur.

Maç Boyunca Tespit Edilen Toplam İstatistikler:
- Tehlikeli Atak: {total_dangerous}
- Hızlı Geçiş: {total_transitions}
- Ceza Sahası Girişi: {total_box}

Bölümlere Göre Eğilimler:
{trends_text}

Analistin kendi gözlemleriyle birleştirebilmesi için 3 ana başlıktan oluşan bir taslak hazırla:
1. Genel Maç Akışı
2. Hücum Etkinliği ve Geçişler
3. Dikkat Çeken Taktiksel Eğilimler
"""

    return await _call_nvidia(prompt)


async def generate_comparison_summary(
    comparison_data: Dict[str, Any],
) -> str:
    """Generate a summary explaining the AI vs Human comparison results."""

    prompt = f"""
Yapay zeka (AI) tespitleri ile İnsan Analist gözlemleri arasındaki karşılaştırma sonuçları aşağıdadır:

- Toplam AI Olayı: {comparison_data.get('total_engine_events')}
- Toplam Analist Olayı: {comparison_data.get('total_analyst_events')}
- Ortak Tespit (Örtüşen): {comparison_data.get('overlapping_events')}
- Sadece AI Tespit Etti (Analistin kaçırdığı olabilir): {comparison_data.get('engine_only_events')}
- Sadece Analist Tespit Etti (AI'nin kaçırdığı): {comparison_data.get('analyst_only_events')}
- Anlaşma Oranı: %{int(comparison_data.get('agreement_ratio', 0) * 100)}

Lütfen analiste yönelik, bu karşılaştırmayı değerlendiren yapıcı bir özet yaz (2-3 paragraf).
Amacımız analistin kendi kör noktalarını fark etmesine ve AI sisteminin sınırlarını anlamasına yardımcı olmaktır.
"""

    return await _call_nvidia(prompt)


async def _call_nvidia(prompt: str) -> str:
    """
    Make HTTP request to NVIDIA NIM API (OpenAI-compatible).
    Uses GLM-5.1 model with reasoning capabilities.
    """
    url = f"{settings.NVIDIA_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 2048,
        "stream": False,
        "extra_body": {
            "chat_template_kwargs": {
                "enable_thinking": True,
                "clear_thinking": False
            }
        }
    }

    try:
        async with httpx.AsyncClient(timeout=settings.NVIDIA_TIMEOUT) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract response from OpenAI-compatible format
            choices = data.get("choices", [])
            if not choices:
                logger.error(f"NVIDIA API returned no choices: {data}")
                return "[Yapay Zeka Hatası] Yanıt alınamadı."

            message = choices[0].get("message", {})
            content = message.get("content", "").strip()

            if not content:
                logger.error(f"NVIDIA API returned empty content: {data}")
                return "[Yapay Zeka Hatası] Boş yanıt alındı."

            return content

    except httpx.HTTPStatusError as exc:
        logger.error(f"NVIDIA API HTTP error {exc.response.status_code}: {exc.response.text}")
        return (
            f"[Yapay Zeka Bağlantı Hatası] NVIDIA API'ye ulaşılamadı (HTTP {exc.response.status_code}). "
            f"Lütfen API anahtarınızı ve bağlantınızı kontrol edin."
        )
    except httpx.RequestError as exc:
        logger.error(f"NVIDIA API request error: {exc}")
        return (
            f"[Yapay Zeka Bağlantı Hatası] NVIDIA API'ye bağlanılamadı. "
            f"İnternet bağlantınızı kontrol edin. ({settings.NVIDIA_BASE_URL})"
        )
    except Exception as exc:
        logger.exception(f"NVIDIA API unexpected error: {exc}")
        return "[Yapay Zeka Hatası] Yanıt işlenirken beklenmeyen bir sorun oluştu."
