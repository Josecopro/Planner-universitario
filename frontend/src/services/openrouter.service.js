// OpenRouter API service for AI-powered feedback generation
// Using Polaris Alpha model for educational insights

const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions';
const MODEL = 'anthropic/claude-3.5-sonnet'; // Using a reliable model, can be changed to polaris-alpha when available

/**
 * Generates AI-powered feedback for student performance
 * @param {Object} data - Performance data including grades and submissions
 * @returns {Promise<string>} AI-generated feedback
 */
export async function generatePerformanceFeedback(data) {
  const { estudiante, actividad, calificacion, promedio_grupo } = data;
  
  const apiKey = import.meta.env.VITE_OPENROUTER_API_KEY;
  
  if (!apiKey) {
    console.warn('⚠️ OpenRouter API key not configured');
    return generateFallbackFeedback(data);
  }

  const prompt = `Eres un asistente educativo experto. Analiza el siguiente desempeño de un estudiante y proporciona retroalimentación constructiva en español (máximo 100 palabras):

Estudiante: ${estudiante}
Actividad: ${actividad}
Calificación obtenida: ${calificacion}/5.0
Promedio del grupo: ${promedio_grupo}/5.0

Proporciona retroalimentación breve y constructiva enfocada en:
1. Reconocimiento si la calificación es buena
2. Áreas de mejora si está por debajo del promedio
3. Sugerencias concretas para el profesor`;

  try {
    const response = await fetch(OPENROUTER_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': window.location.origin,
        'X-Title': 'Planner Universitario'
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 200,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ OpenRouter API error:', response.status, errorText);
      return generateFallbackFeedback(data);
    }

    const result = await response.json();
    const feedback = result.choices?.[0]?.message?.content;
    
    if (!feedback) {
      console.warn('⚠️ No feedback generated, using fallback');
      return generateFallbackFeedback(data);
    }

    console.log('✅ AI feedback generated successfully');
    return feedback;
  } catch (error) {
    console.error('❌ Error generating AI feedback:', error);
    return generateFallbackFeedback(data);
  }
}

/**
 * Generates AI-powered insights for overall group performance
 * @param {Object} groupData - Group statistics and performance data
 * @returns {Promise<string>} AI-generated insights
 */
export async function generateGroupInsights(groupData) {
  const { 
    nombre_grupo, 
    total_estudiantes, 
    promedio_general, 
    tasa_entrega,
    actividades_completadas,
    actividades_totales
  } = groupData;
  
  const apiKey = import.meta.env.VITE_OPENROUTER_API_KEY;
  
  if (!apiKey) {
    console.warn('⚠️ OpenRouter API key not configured');
    return generateFallbackGroupInsights(groupData);
  }

  const prompt = `Eres un asistente educativo experto. Analiza el siguiente desempeño grupal y proporciona insights en español (máximo 120 palabras):

Grupo: ${nombre_grupo}
Total de estudiantes: ${total_estudiantes}
Promedio general del grupo: ${promedio_general}/5.0
Tasa de entrega: ${tasa_entrega}%
Actividades completadas: ${actividades_completadas}/${actividades_totales}

Proporciona un análisis breve que incluya:
1. Evaluación general del desempeño del grupo
2. Aspectos destacables (positivos o negativos)
3. Recomendaciones específicas para el profesor para mejorar el rendimiento del grupo`;

  try {
    const response = await fetch(OPENROUTER_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': window.location.origin,
        'X-Title': 'Planner Universitario'
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 250,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ OpenRouter API error:', response.status, errorText);
      return generateFallbackGroupInsights(groupData);
    }

    const result = await response.json();
    const insights = result.choices?.[0]?.message?.content;
    
    if (!insights) {
      console.warn('⚠️ No insights generated, using fallback');
      return generateFallbackGroupInsights(groupData);
    }

    console.log('✅ AI group insights generated successfully');
    return insights;
  } catch (error) {
    console.error('❌ Error generating AI insights:', error);
    return generateFallbackGroupInsights(groupData);
  }
}

/**
 * Fallback feedback generator when AI is not available
 */
function generateFallbackFeedback(data) {
  const { estudiante, calificacion, promedio_grupo } = data;
  
  if (calificacion >= promedio_grupo) {
    return `${estudiante} ha mostrado un buen desempeño en esta actividad, obteniendo una calificación de ${calificacion} que está en o por encima del promedio del grupo (${promedio_grupo}). Continúe motivando este nivel de trabajo.`;
  } else if (calificacion >= promedio_grupo - 0.5) {
    return `${estudiante} obtuvo ${calificacion}, ligeramente por debajo del promedio del grupo (${promedio_grupo}). Considere ofrecer retroalimentación adicional para ayudar a cerrar esta brecha.`;
  } else {
    return `${estudiante} necesita apoyo adicional. Su calificación de ${calificacion} está significativamente por debajo del promedio del grupo (${promedio_grupo}). Recomendación: Programar una tutoría o proporcionar recursos complementarios.`;
  }
}

/**
 * Fallback group insights generator when AI is not available
 */
function generateFallbackGroupInsights(groupData) {
  const { promedio_general, tasa_entrega, actividades_completadas, actividades_totales } = groupData;
  
  let insights = '';
  
  if (promedio_general >= 4.0) {
    insights = `El grupo muestra un excelente desempeño académico con un promedio de ${promedio_general}. `;
  } else if (promedio_general >= 3.5) {
    insights = `El grupo mantiene un desempeño satisfactorio con un promedio de ${promedio_general}. `;
  } else {
    insights = `El grupo requiere atención especial, con un promedio de ${promedio_general}. `;
  }
  
  if (tasa_entrega >= 80) {
    insights += `La tasa de entrega del ${tasa_entrega}% es muy positiva. `;
  } else if (tasa_entrega >= 60) {
    insights += `La tasa de entrega del ${tasa_entrega}% puede mejorar. `;
  } else {
    insights += `La baja tasa de entrega del ${tasa_entrega}% requiere intervención inmediata. `;
  }
  
  insights += `Actividades completadas: ${actividades_completadas}/${actividades_totales}. `;
  insights += 'Recomendación: Mantener comunicación activa con estudiantes de bajo rendimiento.';
  
  return insights;
}
