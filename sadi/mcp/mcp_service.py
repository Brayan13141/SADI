# mcp/mcp_service.py
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from django.conf import settings
import logging
import gc
import re

logger = logging.getLogger(__name__)

class OptimizedSpanishMCPService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_loaded = False
        
        # MODELO RECOMENDADO - Cambia esta línea según tu elección
        self.model_id = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'  # Mantenemos TinyLlama por ahora
    
    def load_model(self):
        """Carga el modelo optimizado para español"""
        if self.is_loaded:
            return
            
        try:
            logger.info(f"🚀 Cargando {self.model_id}...")
            
            torch.set_grad_enabled(False)
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                cache_dir="./model_cache"
            )
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32,
                device_map=None,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
            )
            
            self.model = self.model.to('cpu')
            self.model.eval()
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=1024,
                temperature=0.3,  # Más bajo para menos creatividad
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            
            self.is_loaded = True
            logger.info("✅ Modelo cargado correctamente")
            
            gc.collect()
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            self.setup_fallback()
    
    def setup_fallback(self):
        self.is_loaded = True
    
    def generate_contextual_response(self, prompt, db_context=""):
        """Genera respuesta optimizada para español y contexto"""
        if not self.is_loaded:
            self.load_model()
        
        # Si no hay contexto válido, respuesta directa
        if not db_context or any(x in db_context for x in ["Error", "No hay", "Consulta general"]):
            return self.get_spanish_fallback(prompt, db_context)
        
        try:
            # PROMPT MEJORADO - Más específico y en español
            spanish_prompt = self.create_spanish_prompt(prompt, db_context)
            
            # Generación con parámetros optimizados
            with torch.no_grad():
                outputs = self.pipeline(
                    spanish_prompt,
                    max_new_tokens=300,
                    num_return_sequences=1,
                    temperature=0.2,  # Muy bajo para máxima precisión
                    top_p=0.7,
                    repetition_penalty=1.5,  # Alto para evitar repetición
                    do_sample=False,  # Desactivado para más consistencia
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            response = outputs[0]['generated_text']
            
            # Extraer respuesta
            if spanish_prompt in response:
                response = response.replace(spanish_prompt, '').strip()
            
            # Limpieza mejorada
            response = self.clean_spanish_response(response)
            
            # Verificar si la respuesta es útil
            if not self.is_useful_response(response, db_context):
                return self.get_contextual_direct_response(prompt, db_context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error en generación: {e}")
            return self.get_contextual_direct_response(prompt, db_context)
    
    def create_spanish_prompt(self, prompt, db_context):
        """Crea prompt optimizado para español"""
        prompt_templates = {
            'proyectos': f"""Responde en español usando SOLO esta información:

INFORMACIÓN DE PROYECTOS:
{db_context}

PREGUNTA: {prompt}

RESPUESTA (solo en español, solo información de arriba):""",

            'metas': f"""Responde en español usando SOLO esta información:

INFORMACIÓN DE METAS:
{db_context}

PREGUNTA: {prompt}

RESPUESTA (solo en español, solo información de arriba):""",

            'actividades': f"""Responde en español usando SOLO esta información:

INFORMACIÓN DE ACTIVIDADES:
{db_context}

PREGUNTA: {prompt}

RESPUESTA (solo en español, solo información de arriba):""",

            'ciclos': f"""Responde en español usando SOLO esta información:

INFORMACIÓN DE CICLOS:
{db_context}

PREGUNTA: {prompt}

RESPUESTA (solo en español, solo información de arriba):"""
        }
        
        prompt_lower = prompt.lower()
        if 'proyecto' in prompt_lower:
            return prompt_templates['proyectos']
        elif 'meta' in prompt_lower or 'objetivo' in prompt_lower:
            return prompt_templates['metas']
        elif 'actividad' in prompt_lower:
            return prompt_templates['actividades']
        elif 'ciclo' in prompt_lower:
            return prompt_templates['ciclos']
        else:
            return f"Responde en español usando SOLO esta información:\n\n{db_context}\n\nPREGUNTA: {prompt}\n\nRESPUESTA:"
    
    def clean_spanish_response(self, response):
        """Limpia respuestas en español"""
        # Eliminar frases en inglés
        english_phrases = [
            "please", "find", "information", "here", "specific", "details",
            "according", "data", "following", "list", "here is", "below"
        ]
        
        for phrase in english_phrases:
            response = re.sub(rf'\b{phrase}\b.*?\.', '', response, flags=re.IGNORECASE)
        
        # Eliminar texto repetitivo o inválido
        invalid_patterns = [
            r"Información general.*",
            r"Consulta general.*",
            r"ℹ️.*INFORMACIÓN DEL SISTEMA.*",
        ]
        
        for pattern in invalid_patterns:
            response = re.sub(pattern, '', response)
        
        # Si la respuesta quedó muy corta, devolver vacío
        if len(response.strip()) < 10:
            return ""
        
        return response.strip()
    
    def is_useful_response(self, response, db_context):
        """Verifica si la respuesta es útil"""
        if not response or len(response) < 15:
            return False
        
        # Verificar que contiene información del contexto
        context_words = set(db_context.lower().split()[:10])
        response_words = set(response.lower().split())
        common_words = context_words.intersection(response_words)
        
        return len(common_words) >= 2
    
    def get_contextual_direct_response(self, prompt, db_context):
        """Respuesta directa en español usando el contexto"""
        prompt_lower = prompt.lower()
        
        if 'proyecto' in prompt_lower:
            return f"🏗️ **TUS PROYECTOS EN SADI:**\n\n{db_context}"
        elif 'meta' in prompt_lower or 'objetivo' in prompt_lower:
            return f"🎯 **TUS METAS EN SADI:**\n\n{db_context}"
        elif 'actividad' in prompt_lower:
            return f"✅ **TUS ACTIVIDADES EN SADI:**\n\n{db_context}"
        elif 'ciclo' in prompt_lower:
            return f"🔄 **CICLOS EN SADI:**\n\n{db_context}"
        else:
            return f"📊 **INFORMACIÓN SOLICITADA:**\n\n{db_context}"
    
    def get_spanish_fallback(self, prompt, db_context):
        """Respuesta de respaldo en español"""
        prompt_lower = prompt.lower()
        
        if 'proyecto' in prompt_lower:
            return "📋 No tengo información de proyectos específica en este momento. Consulta el módulo de Proyectos en SADI."
        elif 'meta' in prompt_lower:
            return "🎯 No puedo acceder a las metas actualmente. Revisa el módulo de Metas en SADI."
        elif 'actividad' in prompt_lower:
            return "✅ No hay información de actividades disponible. Verifica el módulo de Actividades."
        elif 'ciclo' in prompt_lower:
            return "🔄 No tengo datos de ciclos. Consulta el módulo de Programas."
        else:
            return "🤖 No tengo información específica sobre tu consulta."

# Instancia global
mcp_service = OptimizedSpanishMCPService()
