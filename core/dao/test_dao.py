from petercat_utils.db.client.supabase import get_client


client = get_client()

bot_approval = (
    client.table("bot_approval")
    .select("*")
    .eq("bot_id", 1)
    .execute()
)

print(bot_approval)
