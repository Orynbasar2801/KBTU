-- -- вставка/обнобвление (ЗАДАНИЕ 2)
-- create or replace procedure upsert_contact(p_name TEXT, p_phone TEXT)
-- language plpgsql as $$
-- begin
-- 	insert into phonebook (first_name, phone_number) values (p_name, p_phone)
-- 	on conflict (first_name, last_name) do update set phone_number = EXCLUDED.phone_number;
-- end;
-- $$;

-- -- Удаление (Задание 5)
-- create or replace procedure delete_contact(p_val TEXT)
-- language plpgsql as $$
-- begin
-- 	delete from phonebook where first_name = p_val or phone_number = p_val;
-- end;
-- $$;

SELECT * from phonebook