{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "1ca9028f-00d3-4327-9256-4b7e0d76fbfb"
        },
        {
            "Command": "i want a table",
            "Expected": "Right this way!\nThe robot shows you to a wooden table",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "715def20-1fba-41c8-a679-d38f62c867bd"
        },
        {
            "Command": "i want a salad",
            "Expected": "Coming right up!",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "5ddd22cc-9912-4bae-87e9-6af5d96aa3cb"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "96508b3a-1875-429e-b139-8c55ba8bb366"
        },
        {
            "Command": "i want a salad",
            "Expected": "Sorry, you must be seated to order",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f42e4ee8-9e14-42f0-86fc-2e2b9d3acd95"
        }
    ]
}