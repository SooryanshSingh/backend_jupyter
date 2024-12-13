const supabaseurl = window.config.SUPABASE_URL 
const supabasekey = window.config.SUPABASE_KEY

const supabaseclient = supabase.createClient(supabaseurl, supabasekey);
console.log(supabase);
console.log(supabaseurl, supabasekey);

document.getElementById('signin-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('signin-email').value.trim();
    const password = document.getElementById('signin-password').value.trim();
  
    const { session, error } = await supabaseclient.auth.signInWithPassword({
      email,
      password,
    });
  
    if (error) {
      alert('Error logging in: ' + error.message);
    } else {
      alert('Login successful!');
      console.log('Session:', session);
      window.location.href = '/homepage'; 
    }
});
