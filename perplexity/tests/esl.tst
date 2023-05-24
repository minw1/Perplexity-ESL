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
            "Expected": "Robot: Right this way!\nThe robot shows you to a wooden table\nRobot: I hope you have a lovely dining experience with us today. Make sure to ask your waiter for the specials!\nA minute passes \nRobot Waiter: Hello! How can I help you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "715def20-1fba-41c8-a679-d38f62c867bd"
        },
        {
            "Command": "i want a salad",
            "Expected": "Excellent Choice! Can I get you anything else?",
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
            "Expected": "Robot: Right this way!\nThe robot shows you to a wooden table\nRobot: I hope you have a lovely dining experience with us today. Make sure to ask your waiter for the specials!\nA minute passes \nRobot Waiter: Hello! How can I help you?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x8,_table_n_1(x8),pronoun_q(x3,pron(x3),_give_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "55ab1659-281d-4af5-9f82-ff01e39cb6b5"
        },
        {
            "Command": "give me a salad",
            "Expected": "Excellent Choice! Can I get you anything else?",
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
            "Expected": "Robot: Right this way!\nThe robot shows you to a wooden table\nRobot: I hope you have a lovely dining experience with us today. Make sure to ask your waiter for the specials!\nA minute passes \nRobot Waiter: Hello! How can I help you?",
            "Tree": "_would_v_modal(e2,_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_like_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "3c72d3c2-663c-4593-8705-92b42f26a21f"
        },
        {
            "Command": "I would like a salad",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_would_v_modal(e2,_a_q(x11,_salad_n_1(x11),pronoun_q(x3,pron(x3),_like_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "05295d60-471a-4adc-926e-d642fcfa44f0"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "7a733718-c7a1-46a9-8957-8c562b7c8cf2"
        },
        {
            "Command": "could i have a soup?",
            "Expected": "Sorry, you must be seated to order",
            "Tree": "_could_v_modal(e2,_a_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "5176e174-c274-4db7-9cfb-07e8b0593c07"
        },
        {
            "Command": "could i have a table?",
            "Expected": "Robot: Right this way!\nThe robot shows you to a wooden table\nRobot: I hope you have a lovely dining experience with us today. Make sure to ask your waiter for the specials!\nA minute passes \nRobot Waiter: Hello! How can I help you?",
            "Tree": "_could_v_modal(e2,_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "c1ea414c-2a6e-46a1-b683-519af8ecaa6b"
        },
        {
            "Command": "could i have a soup?",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_could_v_modal(e2,_a_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "77c115f7-6d33-4f8c-b4fb-ae6fa743a146"
        },
        {
            "Command": "could i have a table?",
            "Expected": "Um... You're at a table",
            "Tree": "_could_v_modal(e2,_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "6ded92f5-70e8-4d06-b6c3-530c12fc78c9"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "44ecdeaa-5b06-4d41-af4d-172792e5e854"
        },
        {
            "Command": "please, can I have a table",
            "Expected": "Robot: Right this way!\nThe robot shows you to a wooden table\nRobot: I hope you have a lovely dining experience with us today. Make sure to ask your waiter for the specials!\nA minute passes \nRobot Waiter: Hello! How can I help you?",
            "Tree": "[polite(please,i5,e2), _can_v_modal(e2,_a_q(x13,_table_n_1(x13),pronoun_q(x3,pron(x3),_have_v_1(e12,x3,x13))))]",
            "Enabled": true,
            "ID": "84838235-e3ec-49c6-9d23-7fde183a9a66"
        },
        {
            "Command": "please, can I have a soup?",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "[polite(please,i5,e2), _can_v_modal(e2,_a_q(x13,_soup_n_1(x13),pronoun_q(x3,pron(x3),_have_v_1(e12,x3,x13))))]",
            "Enabled": true,
            "ID": "174208d7-868c-4bf4-b810-c6726d924990"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "b07ae6e3-85db-48f2-a330-ebd8e9175745"
        },
        {
            "Command": "i could want a soup",
            "Expected": "Sorry, you must be seated to order",
            "Tree": "_could_v_modal(e2,_a_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "51d16d4d-0491-4d09-930e-d8143315bafa"
        },
        {
            "Command": "i could want a table",
            "Expected": "Robot: Right this way!\nThe robot shows you to a wooden table\nRobot: I hope you have a lovely dining experience with us today. Make sure to ask your waiter for the specials!\nA minute passes \nRobot Waiter: Hello! How can I help you?",
            "Tree": "_could_v_modal(e2,_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "a007eda8-42e2-49a4-85f7-b8a92fe172e6"
        },
        {
            "Command": "i could have a tabble",
            "Expected": "I don't know the words: tabble/nn",
            "Tree": "None",
            "Enabled": true,
            "ID": "274b74e0-a5c6-439d-83d3-d7c4b1a8032d"
        },
        {
            "Command": "i could have a table",
            "Expected": "Um... You're at a table",
            "Tree": "_could_v_modal(e2,_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "1ce964ae-7303-4d32-9dae-ffc8cfa8f26f"
        },
        {
            "Command": "what are the specials today?",
            "Expected": "('soup1',)('salad1',)",
            "Tree": "def_implicit_q(x14,[time_n(x14), _today_a_1(e19,x14)],which_q(x5,thing(x5),_the_q(x3,[_special_n_1(x3), loc_nonsp(e13,x3,x14)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "cb38d91c-4ad5-432e-8930-9849ab7019de"
        },
        {
            "Command": "i would like a table today",
            "Expected": "Um... You're at a table",
            "Tree": "_would_v_modal(e2,_a_q(x11,_table_n_1(x11),def_implicit_q(x17,[time_n(x17), _today_a_1(e22,x17)],pronoun_q(x3,pron(x3),[loc_nonsp(e16,e10,x17), _like_v_1(e10,x3,x11)]))))",
            "Enabled": true,
            "ID": "4bbf8169-3ea6-43c7-93b6-8f1070faf40e"
        },
        {
            "Command": "could i have a salad today",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_could_v_modal(e2,_a_q(x11,_salad_n_1(x11),def_implicit_q(x17,[time_n(x17), _today_a_1(e22,x17)],pronoun_q(x3,pron(x3),[loc_nonsp(e16,e10,x17), _have_v_1(e10,x3,x11)]))))",
            "Enabled": true,
            "ID": "9de64934-cdc9-45f3-ba14-8f7e4421151c"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "ee00db49-d717-467a-a25f-a9ef79746c1a"
        },
        {
            "Command": "what's on the menu?'",
            "Expected": "('steak1',)",
            "Tree": "which_q(x3,thing(x3),_the_q(x8,_menu_n_1(x8),_on_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "354751bb-de4b-495b-a582-2481669c1ae1"
        },
        {
            "Command": "what food is on the menu?",
            "Expected": "('steak1',)",
            "Tree": "_which_q(x3,_food_n_1(x3),_the_q(x8,_menu_n_1(x8),_on_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c7ec0bb5-ae28-442a-8e60-f62ab503244e"
        },
        {
            "Command": "what steak is on the menu?",
            "Expected": "('steak1',)",
            "Tree": "_which_q(x3,_steak_n_1(x3),_the_q(x8,_menu_n_1(x8),_on_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "0c0a76e5-cae2-4970-a982-06032c3a16eb"
        },
        {
            "Command": "i want a table",
            "Expected": "Robot: Right this way!\nThe robot shows you to a wooden table\nRobot: I hope you have a lovely dining experience with us today. Make sure to ask your waiter for the specials!\nA minute passes \nRobot Waiter: Hello! How can I help you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "b4b0c5c3-3fd4-4dad-98c8-080b09f080e4"
        },
        {
            "Command": "i would like a salad",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_would_v_modal(e2,_a_q(x11,_salad_n_1(x11),pronoun_q(x3,pron(x3),_like_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "2a68e0fa-4dfc-4213-8f3b-9a3ea695ca5d"
        },
        {
            "Command": "i would like the check please",
            "Expected": "Your total is 3 dollars. Would you like to pay by cash or card?",
            "Tree": "_would_v_modal(e2,_the_q(x11,_check_n_of(x11,i16),pronoun_q(x3,pron(x3),[_please_a_1(e17,e10), _like_v_1(e10,x3,x11)])))",
            "Enabled": true,
            "ID": "2ea04da8-107f-402b-b967-e0bac745e264"
        },
        {
            "Command": "could i get a table please",
            "Expected": "Um... You're at a table",
            "Tree": "_could_v_modal(e2,_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),[_please_a_1(e16,e10), _get_v_1(e10,x3,x11)])))",
            "Enabled": true,
            "ID": "c3dd6d92-de46-4ea1-a7c3-25ee8f55f54e"
        },
        {
            "Command": "i want a salad",
            "Expected": "Sorry, you got the last one of those. We don't have any more.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "cb6be651-74fe-40a7-8e8f-c50d9344b132"
        },
        {
            "Command": "check, please",
            "Expected": "Your total is 3 dollars. Would you like to pay by cash or card?",
            "Tree": "pronoun_q(x3,pron(x3),[_please_a_1(e9,e2), _check_v_1(e2,x3,i8)])",
            "Enabled": true,
            "ID": "2301e651-e1eb-46bd-aa90-ea5138898b07"
        },
        {
            "Command": "card",
            "Expected": "Ah. Perfect!",
            "Tree": "udef_q(x4,_card_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "08fd4e97-26b3-458c-9c6e-38a36677703b"
        }
    ]
}