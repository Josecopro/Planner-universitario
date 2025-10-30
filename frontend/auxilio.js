import { supabase } from './supabaseClient'

async function fetchCourses() {
  const { data, error } = await supabase.from('courses').select('*')
  if (error) console.error(error)
  else console.log(data)
}

fetchCourses()


async function testConnection() {
  const { data, error } = await supabase.from('courses').select('*')
  if (error) console.error('❌ Error:', error)
  else console.log('✅ Cursos:', data)
}

testConnection()
