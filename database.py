async def start(message: types.Message):

    user = message.from_user

    if user.id == ADMIN_ID:
        await message.answer("Admin panel:", reply_markup=admin_menu())
        return

    conn = await asyncpg.connect(DATABASE_URL)

    existing = await conn.fetchrow(
        "SELECT * FROM clients WHERE user_id=$1",
        user.id
    )

    if not existing:
        await conn.execute("""
            INSERT INTO clients (user_id, name, confirmed_amount, payments)
            VALUES ($1, $2, 0, 0)
        """, user.id, user.full_name)

    await conn.close()

    await message.answer("Mijoz panel:", reply_markup=client_menu())