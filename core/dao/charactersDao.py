from core.dao.BaseDAO import BaseDAO
from supabase.client import Client

from core.models.bot import BotModel
from petercat_utils.db.client.supabase import get_client

from core.models.characters import CharactersModel


class CharactersDao(BaseDAO):
  client: Client

  def __init__(self):
      super().__init__()
      self.client = get_client()

  def get_bot(self, character_id: str):
    resp = self.client.table("characters")\
      .select("*") \
      .eq("id", character_id) \
      .execute()
    bot = resp.data[0]
    return BotModel(**bot)

  def list(self):
      resp = self.client.table("characters") \
          .select("*") \
          .execute()
      list = resp.data
      return list

  def create(self, characters: CharactersModel):
      charactersRes = self.client.table("characters") \
          .insert(characters.model_dump(exclude=["id"])) \
          .execute()
      return charactersRes

  def delete(self, characters: CharactersModel):
      self.client.table("characters") \
          .delete() \
          .eq("id", characters.id) \
          .execute()

  def update(self, characters: CharactersModel):
      charactersRes = self.client.table("characters") \
                            .update(characters.model_dump(exclude=["id"])) \
                            .eq("id",characters.id) \
                            .execute()

      return charactersRes


