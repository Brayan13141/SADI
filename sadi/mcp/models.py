# mcp/models.py
from django.db import models
from django.conf import settings  # ¡Importante!

class MCPConversation(models.Model):
    # Usa settings.AUTH_USER_MODEL en lugar de User directo
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Esto es lo correcto
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user}"

class MCPMessage(models.Model):
    conversation = models.ForeignKey(
        MCPConversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        role = "Usuario" if self.is_user else "Asistente"
        return f"{role}: {self.content[:50]}..."

class ReportTemplate(models.Model):
    name = models.CharField(max_length=100)
    template_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
