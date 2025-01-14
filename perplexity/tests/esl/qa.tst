{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "d5f8a208-b881-4dae-a1b6-5fdfe526a1fb"
        },
        {
            "Command": "what do you have?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "4c77d27e-6a16-4ca3-84d6-bee985bb5ced"
        },
        {
            "Command": "what is meat?",
            "Expected": "If you'd like to hear about our menu items, you'll need to have a seat.",
            "Tree": "which_q(x5,thing(x5),udef_q(x3,_meat_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "65845078-909d-44bc-b3b8-44e37abfeadf"
        },
        {
            "Command": "what is the bill?",
            "Expected": "Let's talk about the bill once you've finished eating.",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_bill_n_of(x3,i13),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "d6b53f06-71c4-4ffb-9152-5e41635d1197"
        },
        {
            "Command": "how much is the soup?",
            "Expected": "Let's talk about prices once you've been seated.",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "36d590b3-0f4d-4bc2-958e-33fc650e9a12"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "80341a0a-1e99-486f-a6ee-bca27cc2066f"
        },
        {
            "Command": "I'd like a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(2,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "66b5319c-66be-4787-b97b-4db8ea2effe5"
        },
        {
            "Command": "how much is the soup?",
            "Expected": "4 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "475bb0be-38e8-4ac5-b9c1-d4822dafa8b8"
        }
    ]
}