const supabaseUrl = window.config.SUPABASE_URL; 
const supabaseKey = window.config.SUPABASE_KEY;

const supabaseclient = supabase.createClient(supabaseUrl, supabaseKey)
console.log(supabase)
console.log(supabaseUrl, supabaseKey);

// signup logic
document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value.trim();

  const { user, error } = await supabaseclient.auth.signUp({
    email,
    password,
  });

  if (error) {
    console.log(error)

    if (error.message.includes('already registered')) {
      alert('This email is already registered, Please sign in or use a different email.')
    }
     
    else {
      alert('Error signing up: ' + error.message)
    }
  }
  
  else {
    console.log('User created:', user);
    alert('Sign-up successful! Check your email for confirmation.')
  }
})
