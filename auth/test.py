from petercat_utils import get_client, get_env_variable
supabase = get_client()
print(supabase)
res = supabase.table("profiles").upsert({ "id" : 1   }).execute()
print(res)

