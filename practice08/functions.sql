-- 1. Поиск (Задание 1)
CREATE OR REPLACE FUNCTION search_contacts(p_pattern TEXT)
RETURNS TABLE (id INT, first_name VARCHAR, last_name VARCHAR, phone_number VARCHAR) 
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY 
    SELECT p.id, p.first_name, p.last_name, p.phone_number 
    FROM phonebook p 
    WHERE p.first_name ILIKE '%' || p_pattern || '%' 
       OR p.last_name ILIKE '%' || p_pattern || '%'
       OR p.phone_number LIKE p_pattern || '%';
END;
$$;

-- 4. Пагинация (Задание 4)
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE (id INT, first_name VARCHAR, last_name VARCHAR, phone_number VARCHAR) 
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY 
    SELECT p.id, p.first_name, p.last_name, p.phone_number 
    FROM phonebook p 
    LIMIT p_limit OFFSET p_offset;
END;
$$;