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
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "713d2afb-73bf-4212-8525-4253492204fd"
        },
        {
            "Command": "give me a table",
            "Expected": "Right this way!\nThe robot shows you to a wooden table",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x8,_table_n_1(x8),pronoun_q(x3,pron(x3),_give_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "55ab1659-281d-4af5-9f82-ff01e39cb6b5"
        },
        {
            "Command": "give me a salad",
            "Expected": "Coming right up!",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x8,_salad_n_1(x8),pronoun_q(x3,pron(x3),_give_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "518d7323-ecc1-4b03-83b5-8665f2896686"
        },
        {
            "Command": "give me a table",
            "Expected": "Um... You're at a table",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x8,_table_n_1(x8),pronoun_q(x3,pron(x3),_give_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "65836ed2-d798-4120-8870-91c215cdb811"
        },
        {
            "Command": "i want a table",
            "Expected": "Um... You're at a table",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c46fcc1a-0a17-4345-938d-20307e0baad6"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "eef5f0e8-fd5b-4118-accb-c2cf21072b9b"
        },
        {
            "Command": "I would like a salad",
            "Expected": "Sorry, you must be seated to order",
            "Tree": "_would_v_modal(e2,_a_q(x11,_salad_n_1(x11),pronoun_q(x3,pron(x3),_like_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "0590b708-66e8-48fa-ad7c-956b65c0043a"
        },
        {
            "Command": "I would like a table",
            "Expected": "Right this way!\nThe robot shows you to a wooden table",
            "Tree": "_would_v_modal(e2,_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_like_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "3c72d3c2-663c-4593-8705-92b42f26a21f"
        },
        {
            "Command": "I would like a salad",
            "Expected": "Coming right up!",
            "Tree": "_would_v_modal(e2,_a_q(x11,_salad_n_1(x11),pronoun_q(x3,pron(x3),_like_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "05295d60-471a-4adc-926e-d642fcfa44f0"
        }
    ]
}