/*
  # Add trigger to auto-create user profile on signup
  
  1. Purpose
    - Automatically creates a user_profiles entry when a new user signs up
    - Syncs user metadata from auth.users to user_profiles table
  
  2. Implementation
    - Creates a PL/pgSQL function that runs on auth.users INSERT
    - Extracts name, age, and city from user_metadata (raw_user_meta_data)
    - Inserts into user_profiles with proper error handling
*/

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE PLPGSQL SECURITY DEFINER SET search_path = PUBLIC AS $$
BEGIN
  INSERT INTO public.user_profiles (id, name, age, city)
  VALUES (
    NEW.id,
    COALESCE((NEW.raw_user_meta_data->>'name'), 'User'),
    COALESCE((NEW.raw_user_meta_data->>'age')::INTEGER, 18),
    COALESCE((NEW.raw_user_meta_data->>'city'), 'Unknown')
  )
  ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    age = EXCLUDED.age,
    city = EXCLUDED.city,
    updated_at = NOW();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
