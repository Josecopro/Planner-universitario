from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from src.models import (
    Student, StudentCreate, Activity, ActivityCreate, ActivityUpdate,
    DashboardData, DashboardStats, WeeklyProgress, GradeDistribution, Alert,
    Message, MessageCreate, User, ApiResponse
)

app = FastAPI()

app.title = "Planner Universitario"
app.description = "API para el sistema de planner universitario"
app.version = "1.0.0"

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

students_db = [
    {
        "id": 1,
        "name": "María González",
        "email": "maria.gonzalez@universidad.edu",
        "career": "Ingeniería en Sistemas",
        "semester": 6,
        "status": "active",
        "avatar": "M"
    },
    {
        "id": 2,
        "name": "Carlos Rodríguez",
        "email": "carlos.rodriguez@universidad.edu",
        "career": "Administración de Empresas",
        "semester": 4,
        "status": "active",
        "avatar": "C"
    },
    {
        "id": 3,
        "name": "Ana López",
        "email": "ana.lopez@universidad.edu",
        "career": "Psicología",
        "semester": 8,
        "status": "inactive",
        "avatar": "A"
    },
    {
        "id": 4,
        "name": "Diego Martínez",
        "email": "diego.martinez@universidad.edu",
        "career": "Medicina",
        "semester": 10,
        "status": "active",
        "avatar": "D"
    }
]

activities_db = [
    {
        "id": 1,
        "title": "Tarea de Cálculo Diferencial",
        "subject": "Cálculo I",
        "description": "Resolver ejercicios del capítulo 3: Derivadas",
        "due_date": "2025-09-20",
        "priority": "high",
        "status": "pending",
        "category": "tarea",
        "estimated_hours": 3,
        "tags": ["matemáticas", "derivadas"],
        "created_at": "2025-09-15"
    },
    {
        "id": 2,
        "title": "Ensayo sobre la Revolución Industrial",
        "subject": "Historia Universal",
        "description": "Redactar un ensayo de 1500 palabras sobre el impacto social de la Revolución Industrial",
        "due_date": "2025-09-25",
        "priority": "medium",
        "status": "in-progress",
        "category": "ensayo",
        "estimated_hours": 5,
        "tags": ["historia", "ensayo"],
        "created_at": "2025-09-12"
    },
    {
        "id": 3,
        "title": "Laboratorio de Química Orgánica",
        "subject": "Química",
        "description": "Práctica de síntesis de compuestos orgánicos",
        "due_date": "2025-09-18",
        "priority": "high",
        "status": "completed",
        "category": "laboratorio",
        "estimated_hours": 4,
        "tags": ["química", "laboratorio"],
        "created_at": "2025-09-10"
    }
]

messages_db = [
    {
        "id": 1,
        "sender": "María González",
        "content": "¡Hola! ¿Alguien ha terminado la tarea de Cálculo?",
        "timestamp": "10:30 AM",
        "is_own": False,
        "avatar": "M"
    },
    {
        "id": 2,
        "sender": "Tú",
        "content": "Sí, ya la terminé. ¿Necesitas ayuda con algún ejercicio?",
        "timestamp": "10:32 AM",
        "is_own": True,
        "avatar": "T"
    },
    {
        "id": 3,
        "sender": "Carlos Rodríguez",
        "content": "Yo también necesito ayuda con el ejercicio 5 😅",
        "timestamp": "10:35 AM",
        "is_own": False,
        "avatar": "C"
    }
]

@app.get('/')
def get_home():
    return {
        "message": "Bienvenido al API del Planner Universitario",
        "version": "1.0.0",
        "endpoints": [
            "/docs",
            "/students",
            "/activities", 
            "/dashboard",
            "/chat"
        ]
    }

# ============ ENDPOINTS DE ESTUDIANTES ============

@app.get("/students", response_model=List[Student])
def get_students(status: Optional[str] = None):
    """Obtener lista de estudiantes con filtro opcional por estado"""
    if status:
        filtered_students = [s for s in students_db if s["status"] == status]
        return filtered_students
    return students_db

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    """Obtener un estudiante específico por ID"""
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student

@app.post("/students", response_model=Student)
def create_student(student: StudentCreate):
    """Crear un nuevo estudiante"""
    new_id = max([s["id"] for s in students_db]) + 1 if students_db else 1
    new_student = {
        "id": new_id,
        "name": student.name,
        "email": student.email,
        "career": student.career,
        "semester": student.semester,
        "status": student.status,
        "avatar": student.name[0].upper()
    }
    students_db.append(new_student)
    return new_student

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentCreate):
    """Actualizar un estudiante existente"""
    student_index = next((i for i, s in enumerate(students_db) if s["id"] == student_id), None)
    if student_index is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    students_db[student_index].update({
        "name": student.name,
        "email": student.email,
        "career": student.career,
        "semester": student.semester,
        "status": student.status,
        "avatar": student.name[0].upper()
    })
    return students_db[student_index]

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    """Eliminar un estudiante"""
    student_index = next((i for i, s in enumerate(students_db) if s["id"] == student_id), None)
    if student_index is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    deleted_student = students_db.pop(student_index)
    return {"message": f"Estudiante {deleted_student['name']} eliminado correctamente"}

# ============ ENDPOINTS DE ACTIVIDADES ============

@app.get("/activities", response_model=List[Activity])
def get_activities(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    subject: Optional[str] = None
):
    """Obtener lista de actividades con filtros opcionales"""
    filtered_activities = activities_db.copy()
    
    if status:
        filtered_activities = [a for a in filtered_activities if a["status"] == status]
    if priority:
        filtered_activities = [a for a in filtered_activities if a["priority"] == priority]
    if subject:
        filtered_activities = [a for a in filtered_activities if a["subject"] == subject]
    
    return filtered_activities

@app.get("/activities/{activity_id}", response_model=Activity)
def get_activity(activity_id: int):
    """Obtener una actividad específica por ID"""
    activity = next((a for a in activities_db if a["id"] == activity_id), None)
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return activity

@app.post("/activities", response_model=Activity)
def create_activity(activity: ActivityCreate):
    """Crear una nueva actividad"""
    new_id = max([a["id"] for a in activities_db]) + 1 if activities_db else 1
    new_activity = {
        "id": new_id,
        "title": activity.title,
        "subject": activity.subject,
        "description": activity.description,
        "due_date": activity.due_date,
        "priority": activity.priority,
        "status": activity.status,
        "category": activity.category,
        "estimated_hours": activity.estimated_hours,
        "tags": activity.tags,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    activities_db.append(new_activity)
    return new_activity

@app.put("/activities/{activity_id}", response_model=Activity)
def update_activity(activity_id: int, activity: ActivityUpdate):
    """Actualizar una actividad existente"""
    activity_index = next((i for i, a in enumerate(activities_db) if a["id"] == activity_id), None)
    if activity_index is None:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    # Solo actualizar campos que no sean None
    update_data = {k: v for k, v in activity.dict().items() if v is not None}
    activities_db[activity_index].update(update_data)
    
    return activities_db[activity_index]

@app.delete("/activities/{activity_id}")
def delete_activity(activity_id: int):
    """Eliminar una actividad"""
    activity_index = next((i for i, a in enumerate(activities_db) if a["id"] == activity_id), None)
    if activity_index is None:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    deleted_activity = activities_db.pop(activity_index)
    return {"message": f"Actividad '{deleted_activity['title']}' eliminada correctamente"}

# ============ ENDPOINTS DEL DASHBOARD ============

@app.get("/dashboard", response_model=DashboardData)
def get_dashboard_data():
    """Obtener datos del dashboard"""
    # Calcular estadísticas en tiempo real
    active_students = len([s for s in students_db if s["status"] == "active"])
    pending_activities = len([a for a in activities_db if a["status"] == "pending"])
    
    dashboard_data = {
        "stats": {
            "active_students": active_students,
            "general_average": 4.2,
            "pending_submissions": pending_activities,
            "attendance": 78
        },
        "weekly_progress": [
            {"week": "Sem 1", "value": 2.5},
            {"week": "Sem 2", "value": 3.2},
            {"week": "Sem 3", "value": 2.8},
            {"week": "Sem 4", "value": 3.8},
            {"week": "Sem 5", "value": 4.1},
            {"week": "Sem 6", "value": 3.9},
            {"week": "Sem 7", "value": 4.2}
        ],
        "grade_distribution": [
            {"name": "Excelente", "value": 25, "color": "#10B981"},
            {"name": "Bueno", "value": 35, "color": "#932428"},
            {"name": "Regular", "value": 25, "color": "#F59E0B"},
            {"name": "Deficiente", "value": 15, "color": "#EF4444"}
        ],
        "alerts": [
            {
                "id": 1,
                "type": "warning",
                "title": "Estudiante en Riesgo",
                "description": "María González - Bajo rendimiento en últimas 3 actividades",
                "action": "Ver detalles"
            },
            {
                "id": 2,
                "type": "info",
                "title": "Entregas Vencidas",
                "description": f"{pending_activities} actividades pendientes de entrega",
                "action": "Ver actividades"
            }
        ]
    }
    return dashboard_data

# ============ ENDPOINTS DEL CHAT ============

@app.get("/chat/messages", response_model=List[Message])
def get_messages():
    """Obtener todos los mensajes del chat"""
    return messages_db

@app.post("/chat/messages", response_model=Message)
def send_message(message: MessageCreate):
    """Enviar un nuevo mensaje al chat"""
    new_id = max([m["id"] for m in messages_db]) + 1 if messages_db else 1
    new_message = {
        "id": new_id,
        "sender": message.sender,
        "content": message.content,
        "timestamp": datetime.now().strftime("%H:%M"),
        "is_own": message.is_own,
        "avatar": message.sender[0].upper()
    }
    messages_db.append(new_message)
    return new_message

@app.get("/chat/users", response_model=List[User])
def get_active_users():
    """Obtener lista de usuarios activos en el chat"""
    users = [
        {"id": 1, "name": "María González", "status": "online", "avatar": "M"},
        {"id": 2, "name": "Carlos Rodríguez", "status": "online", "avatar": "C"},
        {"id": 3, "name": "Ana López", "status": "away", "avatar": "A"},
        {"id": 4, "name": "Diego Martínez", "status": "offline", "avatar": "D"}
    ]
    return users

# ============ ENDPOINTS AUXILIARES ============

@app.get("/subjects")
def get_subjects():
    """Obtener lista de materias disponibles"""
    subjects = [
        "Cálculo I",
        "Historia Universal", 
        "Química Orgánica",
        "Programación",
        "Marketing Digital",
        "Física",
        "Literatura",
        "Inglés",
        "Estadística"
    ]
    return {"subjects": subjects}

@app.get("/health")
def health_check():
    """Endpoint de verificación de salud del API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "students": len(students_db),
            "activities": len(activities_db),
            "messages": len(messages_db)
        }
    }