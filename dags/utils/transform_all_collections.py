from utils.mongo_utils import get_all_documents, insert_documents
from datetime import datetime

def transform_all_collections():
    print("Iniciando transformaciones...")

    ## ---------- COVID ----------
    raw_covid = get_all_documents("raw_covid")
    processed_covid = []

    for record in raw_covid:
        try:
            date_str = record["date"]
            cases = int(record["cases"])
            deaths = int(record["deaths"])
            recovered = int(record["recovered"])
            active = cases - deaths - recovered

            processed_covid.append({
                "date": datetime.strptime(date_str, "%m/%d/%y").isoformat(),
                "cases": cases,
                "deaths": deaths,
                "recovered": recovered,
                "active": active,
                "mortality_rate": round(deaths / cases, 4) if cases > 0 else 0.0
            })
        except Exception as e:
            print(f"Error procesando record COVID: {e}")

    insert_documents("processed_covid", processed_covid)
    print(f"COVID transformado: {len(processed_covid)} registros")


    ## ---------- POLLUTION ----------
    raw_pollution = get_all_documents("raw_pollution")
    processed_pollution = []

    for r in raw_pollution:
        try:
            fields = r.get("fields", {})
            country = fields.get("country", "Unknown")
            city = fields.get("filename", "Unknown")
            date = fields.get("date") or fields.get("data_dates", "")

            pollutants = {
                "PM25": fields.get("value_pm5") or fields.get("value_pm25"),
                "PM10": fields.get("value_pm10"),
                "CO": fields.get("value_co"),
                "NO2": fields.get("value_no2"),
                "O3": fields.get("value_o3"),
            }

            for pollutant, value in pollutants.items():
                if value is not None:
                    processed_pollution.append({
                        "country": country,
                        "city": city,
                        "pollutant": pollutant,
                        "value": float(value),
                        "date": date,
                        "is_high": float(value) > 100
                    })

        except Exception as e:
            print(f"Error procesando record Pollution: {e}")

    insert_documents("processed_pollution", processed_pollution)
    print(f"Pollution transformado: {len(processed_pollution)} registros")


    ## ---------- WATER (opcional, si Streamlit lo usa luego) ----------
    # Puedes hacer algo similar si decides visualizar datos de raw_water

    print("Transformaciones completadas.")
