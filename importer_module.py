import openpyxl
from datetime import datetime

def parse_date(value):
    """Convierte diferentes formatos de fecha a ISO (YYYY-MM-DD)"""
    if not value:
        return None
    
    # Si ya es un objeto datetime
    if isinstance(value, datetime):
        return value.date().isoformat()
    
    # Si es string
    value = str(value).strip()
    if not value:
        return None
    
    # Intentar varios formatos
    formats = [
        "%Y-%m-%d",      # YYYY-MM-DD
        "%d/%m/%Y",      # DD/MM/YYYY
        "%d-%m-%Y",      # DD-MM-YYYY
        "%Y/%m/%d",      # YYYY/MM/DD
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue
    
    return None

def load_people_from_excel(filepath: str):
    """
    Lee un archivo Excel y retorna una lista de diccionarios con los datos de las personas.
    
    Columnas esperadas:
    - nombre
    - apellido
    - especializacion
    - fecha_expedicion
    - fecha_vencimiento
    - escuela
    - empresa
    - email
    - celular
    """
    wb = openpyxl.load_workbook(filepath)
    sheet = wb.active
    
    # Leer encabezados (primera fila)
    headers = []
    for cell in sheet[1]:
        if cell.value:
            headers.append(str(cell.value).strip().lower())
        else:
            headers.append(None)
    
    # Validar que existen las columnas requeridas
    required = ['nombre', 'apellido', 'especializacion', 'fecha_vencimiento']
    for req in required:
        if req not in headers:
            raise ValueError(f"Falta la columna requerida: {req}")
    
    # Leer datos
    people = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        # Saltar filas vacías
        if not any(row):
            continue
        
        # Crear diccionario con los datos
        person = {}
        for i, header in enumerate(headers):
            if header and i < len(row):
                value = row[i]
                
                # Convertir fechas
                if header in ['fecha_expedicion', 'fecha_vencimiento']:
                    person[header] = parse_date(value)
                else:
                    person[header] = str(value).strip() if value else ""
        
        # Validar que tenga los campos requeridos
        if all(person.get(req) for req in ['nombre', 'apellido', 'especializacion', 'fecha_vencimiento']):
            people.append(person)
    
    wb.close()
    return people