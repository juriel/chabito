export type InputMessageDTO = {
  message: string;
  user_id: string;
  sender_nickname?: string | null;
  sender_jid?: string | null;
  mime_type?: string | null;
  file_base64?: string | null;
};
