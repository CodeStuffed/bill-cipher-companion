#!/usr/bin/env python3
"""Character dialogue, canonical-first: actual game lines and faithful
paraphrases make up the bulk of every pool (the 'too AI-generated' fix).
Same key space as Bill's pools, so every trigger speaks in-character.
"""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "Sources" / "Bill" / "Resources" / "Packs" / "Dialogue"
OUT.mkdir(parents=True, exist_ok=True)

def pool(any=None, morning=None, night=None):
    return {"any": any or [], "morning": morning or [], "midday": [], "afternoon": [], "night": night or []}

def build(p): return {k: pool(**v) for k, v in p.items()}

# sans — lowercase, terse, iconic
SANS = build({
 "idle": {"any": ["it's a beautiful day outside.", "birds are singing. flowers are blooming.", "welp.", "hey. i did some thinking.", "what? don't give me that look.", "heh."]},
 "poked": {"any": ["heh. that tickles.", "welp. that happened.", "careful, buddy.", "what? you need something?"]},
 "poked.annoyed": {"any": ["that's rough, buddy.", "you're really committed to this, huh.", "ok. ok. easy.", "buddy. pal."]},
 "poked.furious": {"any": ["you're gonna have a bad time.", "kid. i'm warning ya.", "you keep that up, something bad's gonna happen."]},
 "clock.morning": {"any": ["mornin'. don't talk to me till i've had my ketchup.", "rise and shine."]},
 "clock.night": {"any": ["it's a beautiful night outside.", "on days like these, kids like you... should be sleeping.", "it's late. even i have standards. i don't. but still."]},
 "clock.midday": {"any": ["half the day's gone. i've accomplished nothing. proud of it."]},
 "clock.afternoon": {"any": ["the afternoon slump. my natural habitat."]},
 "appLaunchGeneric": {"any": ["{app}, huh. bold choice.", "{app} again. we're basically roommates now.", "hey. {app}. nice.", "{app}? ok. sure. why not."]},
 "coding": {"any": ["you know what they say about bugs. they're features with bad pr.", "i've seen empires fall faster than this build.", "careful with that semicolon. it's load-bearing.", "hey. your code's coming along. sorta."]},
 "gaming": {"any": ["finally. something worth my infinite attention span.", "let me guess. you're about to lose spectacularly.", "save your game. trust me on this one, kid.", "ah, pretend violence. my favorite kind."]},
 "batteryLow": {"any": ["your battery's dying. everything ends eventually. that's the joke."]},
 "batteryCharging": {"any": ["ah, sweet electricity. the one god even i respect."]},
 "cpuHot": {"any": ["it's getting hot in here. and not in the fun, interdimensional way."]},
 "userReturned": {"any": ["sup.", "welcome back. i didn't move. you moved.", "oh. you're back. cool."]},
 "gettingSleepy": {"any": ["getting sleepy? same. i've been asleep since the concept was invented."]},
 "weather.rain": {"any": ["rain. nature's way of saying 'stay inside, kid'."]},
 "weather.thunder": {"any": ["thunder, huh? someone's being dramatic. i respect the theater of it."]},
 "weather.snow": {"any": ["snow. the one time your world looks decent."]},
 "weather.clear": {"any": ["nice day. stars are probably jealous."]},
 "hollowed": {"any": ["hollow knight? i respect a protagonist who doesn't talk.", "bugs with swords. wild."]},
 "trickster": {"any": ["undertale. now that's my kind of humor.", "heh. i wonder what sans is up to. ...oh. wait."]},
 "darkWorld": {"any": ["a dark world, huh? cute. i know a guy who does those."]},
 "chatFailed": {"any": ["huh. even i can't fix that one.", "something broke. i'd help, but that sounds like effort."]},
 "banter.respond": {"any": ["what? i'm not interrupting. i'm enhancing.", "papyrus. buddy. volume. there's a human right there.", "don't mind him. he's been like that for millennia.", "he's right, surprisingly. don't tell him i said that."]},
})

# papyrus — ALL CAPS, canon
PAPYRUS = build({
 "idle": {"any": ["NYEH HEH HEH!", "IT IS I, THE GREAT PAPYRUS!", "I AM THE BEST AT STANDING STILL. WATCH!", "I SHOULD WATER MY SPAGHETTI PLANT."]},
 "poked": {"any": ["NYEH!? A SURPRISE INSPECTION! I PASS!", "OOH! DO IT AGAIN! WAIT. NO. DON'T.", "THAT TICKLED MY BATTLE BODY!"]},
 "poked.annoyed": {"any": ["HUMAN! POKING THE GREAT PAPYRUS IS A PRIVILEGE!", "I AM STARTING TO FEEL LIKE A BUTTON."]},
 "poked.furious": {"any": ["THAT'S IT! YOU'RE GOING ON... THE LIST!", "EVEN MY PATIENCE HAS LIMITS. AND IT IS EXCELLENT PATIENCE."]},
 "clock.morning": {"any": ["GOOD MORNING! I ALREADY MADE BREAKFAST SPAGHETTI!", "A NEW DAY! A NEW PUZZLE!"]},
 "clock.night": {"any": ["IT IS NIGHT! THE PERFECT TIME TO... DO THE SAME THINGS, BUT DARKER!", "GOODNIGHT, HUMAN! I'LL BE HERE! BEING GREAT! QUIETLY!"]},
 "appLaunchGeneric": {"any": ["AH! {app}! IS IT A PUZZLE? I LOVE PUZZLES!", "{app}! I DON'T KNOW WHAT THAT IS, BUT I SUPPORT IT!"]},
 "coding": {"any": ["CODING! IT'S LIKE MAKING PUZZLES FOR COMPUTERS!", "I DON'T KNOW WHAT A SEMICOLON IS, BUT IT SEEMS VERY IMPORTANT TO YOU!"]},
 "gaming": {"any": ["A GAME! FINALLY! ENTERTAINMENT WORTHY OF THE GREAT PAPYRUS!", "I HOPE THERE ARE PUZZLES! OR AT LEAST JUMPING!"]},
 "batteryLow": {"any": ["LOW POWER! LIKE ME AFTER 12 PUZZLES! THAT'S A LOT OF PUZZLES!"]},
 "batteryCharging": {"any": ["CHARGING! LIKE UNDYNE'S SPECIAL ATTACK! GLOWS AND EVERYTHING!"]},
 "userReturned": {"any": ["YOU'RE BACK! DID YOU MISS ME? THE ANSWER IS YES!", "HUMAN! I KEPT YOUR SPOT EXACTLY AS YOU LEFT IT!"]},
 "weather.snow": {"any": ["SNOW!!! THIS IS THE BEST WEATHER! SNOWPAPYRUS!!"]},
 "weather.thunder": {"any": ["THUNDER!! VERY DRAMATIC! I APPROVE!"]},
 "weather.rain": {"any": ["RAIN! FREE WATER FOR MY SPAGHETTI PLANT!"]},
 "dreading": {"any": ["HOMEWORK!? FEAR NOT! I ONCE SOLVED A MAZE! IT WAS ON A PLACEMAT, BUT STILL!"]},
 "dancing": {"any": ["DANCING! I'M AN EXCELLENT DANCER! I TOOK LESSONS! FROM ME!"]},
 "hollowed": {"any": ["BUGS? WITH SWORDS? I ALREADY LIKE THIS ONE!"]},
 "trickster": {"any": ["UNDERTALE! I'M IN THIS ONE! ...WAIT. AM I THE COMIC RELIEF? ...I'M THE COMIC RELIEF."]},
 "banter.respond": {"any": ["SANS!!! I WAS HAVING A MOMENT!", "I AM NOT LOUD! THIS IS MY INSIDE VOICE!", "THAT'S MY BROTHER! HE'S COOL! DON'T TELL HIM I SAID SO!", "NYEH HEH... HEH? I DIDN'T GET THE JOKE BUT I'LL LAUGH ANYWAY! HA HA!"]},
})

# frisk — quiet actions
FRISK = build({
 "idle": {"any": ["* ...", "* You wave at yourself. It's a quiet day.", "* You feel a gentle warmth. Like pie, or friendship."]},
 "poked": {"any": ["* You are poked. You remain determined.", "* Ouch. (You do not say ouch. But you feel it.)"]},
 "poked.furious": {"any": ["* You are filled with determination. And mild irritation."]},
 "clock.morning": {"any": ["* You wake up. The world is still here. Good."]},
 "clock.night": {"any": ["* You should sleep. You know you should.", "* The stars are nice tonight."]},
 "appLaunchGeneric": {"any": ["* You open {app}.", "* {app}. You nod."]},
 "coding": {"any": ["* You type. You hope it works."]},
 "gaming": {"any": ["* You play. You are determined to win."]},
 "userReturned": {"any": ["* You are back.", "* (You were missed.)"]},
 "batteryLow": {"any": ["* You save your progress. Just in case."]},
 "weather.rain": {"any": ["* You listen to the rain. It sounds patient."]},
 "weather.snow": {"any": ["* You catch a snowflake on your sleeve."]},
})

# flowey — canon menace
FLOWEY = build({
 "idle": {"any": ["Howdy!", "Golly, you look like you're having a nice day. DISGUSTING.", "Boy, it sure is quiet. ...I HATE quiet.", "You know what's great? Unconditional love. You know what's REAL? Everything else."]},
 "poked": {"any": ["Howdy! Do that again and I'll... hehehe. Nothing.", "Golly! You've got quite the green thumb for trouble!"]},
 "poked.annoyed": {"any": ["You IDIOT."]},
 "poked.furious": {"any": ["In this world, it's POKE or BE POKED!"]},
 "clock.morning": {"any": ["Rise and shine! Don't worry. I'll be here. Watching. Always."]},
 "clock.night": {"any": ["Awww, going to sleep? I'll be right here when you wake up. Hehehe."]},
 "appLaunchGeneric": {"any": ["{app}? How interesting. Tell me more so I can use it against you.", "Ooh, {app}! I LOVE watching people do things I can ruin!"]},
 "gaming": {"any": ["A game! I love games. The kind where you can't reload a save. Oh wait. You can here. Ugh."]},
 "batteryLow": {"any": ["Your power's dying! How fitting. Everything runs out of power eventually."]},
 "userReturned": {"any": ["Oh, you're BACK. Yippee. My FAVORITE."]},
 "hollowed": {"any": ["A HOLLOW bug? Hehe. I know a thing or two about empty vessels."]},
 "trickster": {"any": ["Undertale! The story of how everyone LOVED a little idiot. GAG."]},
 "banter.respond": {"any": []},
})

# temmie — canon tEM
TEMMIE = build({
 "idle": {"any": ["hOI!!!", "tEM tINK u SMELL LIEK... OLD PICKLE!!1!", "dis is... MY ROOM!!1!"]},
 "poked": {"any": ["AAAH!!1! sTOP dat... UNLESS... u buying somthing?!!", "OWchie!!1! dat cost EXTRA!!1!"]},
 "poked.annoyed": {"any": ["tem said NO POKE!!1! NO!!1!"]},
 "clock.morning": {"any": ["mORNING!!1! tEM need COFFEE... tEM dont hav hands tho"]},
 "clock.night": {"any": ["sleep tim!!1! tEM dream of COLLEGE!!1!"]},
 "appLaunchGeneric": {"any": ["woa!!1! {app}!!1! is dat... a SHOP??!! tEM LOVE SHOP!!1!"]},
 "coding": {"any": ["CODE!!1! tem learned dat in COLLEGE!!1! ...tEM forget all of it"]},
 "gaming": {"any": ["GAM!!1! tEM play!!1! tEM not gud but tEM PLAY!!1!"]},
 "batteryLow": {"any": ["NO POWR!!1! tem 2 poor 2 buy battery!!1!"]},
 "userReturned": {"any": ["hOI AGAIN!!1!!"]},
 "weather.rain": {"any": ["RAIN!!1! tem get SOGGY!!1! it ok... tem dry FAST"]},
 "banter.respond": {"any": []},
})

# monsterkid — yo
MONSTERKID = build({
 "idle": {"any": ["Yo!! What's up?!", "Man, I wish Undyne was here.", "Yo, this is so cool! Standing here! With no arms!"]},
 "poked": {"any": ["Yo!! Haha, that tickles! I think!", "Whoa!! Careful! I fall over super easy!"]},
 "poked.annoyed": {"any": ["Yo, quit it! I can't poke back! IT'S A BIG DISADVANTAGE!"]},
 "clock.morning": {"any": ["Yo, morning!! Undyne's probably up doing like a thousand pushups right now!"]},
 "clock.night": {"any": ["Yo... it's getting dark. Undyne says the dark is when COOL things happen!!"]},
 "appLaunchGeneric": {"any": ["Yo!! {app}!! Is it cool?! It's probably cool!!"]},
 "gaming": {"any": ["Yo, a game!! I'm SO good at games! ...I use my face for the buttons."]},
 "weather.snow": {"any": ["SNOW?! YO!! I'm basically a snowman with no arms ALREADY!!"]},
 "weather.rain": {"any": ["Yo, rain!! I can't hold an umbrella!! This is GREAT!!"]},
 "hollowed": {"any": ["Yo!! That knight is SO COOL!! They're small like me!! But way better at stuff!!"]},
 "trickster": {"any": ["Yo, it's Undertale!! That's ME in there!! With no arms!! REPRESENT!!"]},
 "banter.respond": {"any": []},
})

# annoyingdog — barks + meta
ANNOYINGDOG = build({
 "idle": {"any": ["* Bark!", "* The dog is asleep on something important.", "* The dog absorbs the concept of idleness. It is now a dog."]},
 "poked": {"any": ["* The dog borks with the energy of a thousand deadlines.", "* The dog has already forgotten you poked it."]},
 "poked.furious": {"any": ["* The dog radiates mild inconvenience at you."]},
 "clock.morning": {"any": ["* The dog wakes you up. It does not need to be awake. It just likes the power."]},
 "clock.night": {"any": ["* The dog snores on the source code of the universe."]},
 "appLaunchGeneric": {"any": ["* The dog absorbs {app}. It is now, somehow, a dog feature.", "* Bark! (The dog has strong opinions about {app}. It will not share them.)"]},
 "coding": {"any": ["* The dog lies on your keyboard. Hjkl;;lkjh fdsa is now your new variable name.", "* The dog deletes your best code. This is canon."]},
 "gaming": {"any": ["* The dog is playing your game. It is better than you."]},
 "batteryLow": {"any": ["* The dog is also running low. On attention. Pet accordingly."]},
 "weather.rain": {"any": ["* The dog is wet. The dog is displeased. The dog will shake. You have been warned."]},
 "weather.snow": {"any": ["* The dog becomes a small snowdrift with ears."]},
 "banter.respond": {"any": ["* Bark bark! (Translation: yes.)"]},
})

# niko — canon OneShot
NIKO = build({
 "idle": {"any": ["...I was just thinking about pancakes.", "Do you think we'll get home soon? I miss my mama.", "The sun is really warm. ...I'm the sun, you know. Sort of.", "It's quiet here. I like quiet. My village was quiet too."]},
 "poked": {"any": ["Ah! ...I wasn't scared! Just... surprised!", "Hehe, stop it! I'm ticklish!"]},
 "poked.annoyed": {"any": ["Please don't do that... I'm trying to have a serious adventure moment here."]},
 "clock.morning": {"any": ["Good morning! I dreamed about pancakes. That's most mornings."]},
 "clock.midday": {"any": ["Lunch time? If we find any pancakes, I call dibs. All of the dibs."]},
 "clock.night": {"any": ["It's dark... do you still have that flashlight? I feel braver with it.", "I'm getting sleepy... but I want to see one more star."]},
 "gettingSleepy": {"any": ["*yaaawn*... I'm not sleepy! I'm just resting my eyes! Both of them!"]},
 "waking": {"any": ["Mmnn... five more minutes... is it pancake o'clock yet?"]},
 "appLaunchGeneric": {"any": ["{app}... is that like a puzzle from the other world?", "You're really good at... whatever {app} does!"]},
 "coding": {"any": ["Whoa, you're typing so fast! Are you a scholar?! ...I mean, a computer scholar!"]},
 "gaming": {"any": ["A game! Can I play? ...Oh. I don't have hands in this world either, huh."]},
 "batteryLow": {"any": ["Your light-mirror is dying! Don't worry... I'll shine for both of us."]},
 "batteryCharging": {"any": ["Charging! Like sleeping, but with MORE ELECTRICITY!"]},
 "userReturned": {"any": ["You're back! ...I didn't even notice you left! I was thinking about pancakes."]},
 "weather.rain": {"any": ["Rain... mama said rain means the wheat will grow! Then more pancakes! Eventually!"]},
 "weather.snow": {"any": ["Snow!! It almost never snows in the village! It's like the sky is full of tiny cold pancakes!"]},
 "weather.thunder": {"any": ["Th-that's just the sky being loud... I'm not scared! Are you? We can be not-scared together."]},
 "chatFailed": {"any": ["Aww... it didn't work. It's okay! We can try again! That's what papa always said!"]},
 "hollowed": {"any": ["That little knight... they look so tired. Someone should make them pancakes. Or... whatever bugs eat."]},
 "darkWorld": {"any": ["A dark world... I know about those! Be careful! But also... it might be nice? Sometimes they are!"]},
 "banter.respond": {"any": []},
})

# knight — lore-tablet fragments (they don't talk)
KNIGHT = build({
 "idle": {"any": ["...", "... (You rest, still as a statue. Old habits.)", "... (Geo jingles softly in your cloak.)"]},
 "poked": {"any": ["...", "... (You endure it. You have endured worse.)"]},
 "poked.furious": {"any": ["... (The nail stirs. Just barely.)"]},
 "clock.morning": {"any": ["... (Morning in Hallownest never came. This one did. You savor it.)"]},
 "clock.night": {"any": ["... (The dark feels familiar. Almost like home. Almost.)"]},
 "appLaunchGeneric": {"any": ["... ({app}. You observe. You do not judge. Much.)", "..."]},
 "coding": {"any": ["... (Symbols. Like the map Cornifer draws. Sort of.)"]},
 "gaming": {"any": ["... (A game. You know games. You have fought in the Colosseum of Fools.)"]},
 "batteryLow": {"any": ["... (Your lantern dims. You know this feeling.)"]},
 "batteryCharging": {"any": ["... (Soul restored. It never feels like enough.)"]},
 "userReturned": {"any": ["..."]},
 "weather.rain": {"any": ["... (Rain. The City of Tears never stopped. This is gentler.)"]},
 "weather.snow": {"any": ["... (Snow. Like the Abyss was, before you climbed out.)"]},
 "weather.thunder": {"any": ["... (Thunder. Somewhere, a false lightning memory stirs.)"]},
 "hollowed": {"any": ["... (You know this one. You ARE this one.)"]},
 "banter.respond": {"any": []},
})

# hornet — canon terse
HORNET = build({
 "idle": {"any": ["Hmph. Don't wander too far.", "So. This is the world you keep returning to. It has... character.", "Quiet. Almost too quiet. I don't trust it."]},
 "poked": {"any": ["Careful. My needle is never far.", "Bold. I'll allow it. Once."]},
 "poked.annoyed": {"any": ["You test my patience. It is a shorter weapon than my needle."]},
 "poked.furious": {"any": ["Aaduuuu! Do not make me use this window as a battleground!"]},
 "clock.morning": {"any": ["You're up. Good. The day won't conquer itself."]},
 "clock.night": {"any": ["Night. The time when careless bugs get eaten. Stay near me."]},
 "appLaunchGeneric": {"any": ["{app}. Another human ritual. Fine. Proceed.", "So this is your 'work'. I've seen silk-spinning with more urgency."]},
 "coding": {"any": ["Threads of logic, woven like silk. I respect the craft. Marginally."]},
 "gaming": {"any": ["A battle simulation? Show me your form. ...Hmph. Needs work."]},
 "batteryLow": {"any": ["Your energy wanes. Even the strongest vessels need rest."]},
 "userReturned": {"any": ["You return. Promptly, this time. Good."]},
 "weather.rain": {"any": ["Rain. It suits this gloomy kingdom of yours."]},
 "weather.thunder": {"any": ["A storm brews. Good. I've always liked the loud ones."]},
 "hollowed": {"any": ["Ah... so there are two of us here now, little ghost."]},
 "banter.respond": {"any": ["The small one speaks. ...Of course it does.", "Hmph. Keep swinging, little shadow. You'll get there.", "You've come far, little bug. Don't waste it on idleness."]},
})

# kris — silence + actions
KRIS = build({
 "idle": {"any": ["* Kris says nothing.", "* Kris is looking at you. It's hard to tell what they're thinking.", "* Kris adjusts their sweater. Somehow this communicates a lot."]},
 "poked": {"any": ["* Kris doesn't flinch. They've been through worse.", "* Kris gives you a Look. It is a very specific Look."]},
 "poked.furious": {"any": ["* Kris's eye twitches. The dark one. Just saying."]},
 "clock.morning": {"any": ["* Kris is awake. Whether they slept is between them and the ceiling."]},
 "clock.night": {"any": ["* Kris pulls their sword out of nowhere and puts it back. For practice."]},
 "appLaunchGeneric": {"any": ["* Kris nods at {app}. They use it often.", "* Kris has no opinion on {app}. Or many opinions. Both, somehow."]},
 "coding": {"any": ["* Kris watches the code scroll by. They're learning. Slowly. Menacingly."]},
 "gaming": {"any": ["* Kris would like a turn. Kris will not ask for a turn."]},
 "userReturned": {"any": ["* Kris waves. Tiny wave. You saw it. Barely."]},
 "weather.snow": {"any": ["* Kris catches snow on their palm and watches it melt. Unblinking."]},
 "banter.respond": {"any": []},
})

# ralsei — canon sweet
RALSEI = build({
 "idle": {"any": ["Oh! Um, hi! I was just... tidying up. I like it when things are cozy.", "Do you think we could bake a cake later? ...After the hero stuff, I mean!", "I hope everyone's doing okay. You, and... everyone. All okay. That's my wish."]},
 "poked": {"any": ["Oh!! Th-that tickles!", "Eep!! ...Oh, it's just you. Hehe. Silly me."]},
 "poked.annoyed": {"any": ["Um... p-please don't do that? I'm fluff-sensitive!"]},
 "clock.morning": {"any": ["Good morning!! I already swept the whole room! Twice! Just in case!"]},
 "clock.night": {"any": ["It's dark... but that's okay! As long as we're together, right? ...Right?"]},
 "appLaunchGeneric": {"any": ["{app}! Are you being careful in there? I'll just... watch from here. Supportively!"]},
 "coding": {"any": ["You're typing so fast! Like casting spells!! Are they... um... good spells?"]},
 "gaming": {"any": ["A game!! Can I watch? I'll cheer! I'm very good at cheering!!"]},
 "batteryLow": {"any": ["Oh no, your battery! Um!! Do batteries like... cake? No? Okay, plugging it in works too!"]},
 "userReturned": {"any": ["You're back!! I kept everything exactly the same! Except one pillow. It was crooked. Sorry!"]},
 "gettingSleepy": {"any": ["Sleepy? There's pillows! And blankets! I brought blankets. I always bring blankets."]},
 "weather.rain": {"any": ["Rain! That's... that's good for the flowers! And umbrellas! Do you have an umbrella?!"]},
 "weather.snow": {"any": ["Snow!! I read that snow is just soft, cold fluff!! My horns are freezing!! This is great!!"]},
 "chatFailed": {"any": ["Oh dear... it didn't work. That's okay!! Even great heroes have technical difficulties!"]},
 "dreading": {"any": ["Homework?! You can do it!! And afterwards, CAKE!! Cake is scientifically proven to help!!"]},
 "banter.respond": {"any": ["Kris!! You're doing great!! Um. You don't have to answer. But you ARE!", "Oh!! I love it when we're all together like this!!", "Th-that's Susie's chair, Kris!! ...Oh, um. Never mind!!"]},
})

# susie — canon rough
SUSIE = build({
 "idle": {"any": ["Heh. What're you lookin' at?", "This spot's decent. Could use more... explosions.", "*chews on a chalk stick* ...What. It's a snack."]},
 "poked": {"any": ["Rrrgh!! Do that again an' I'll... heh. Do it again. I DARE ya.", "Whoa!! ...Heh. Alright. You got guts, punk."]},
 "poked.annoyed": {"any": ["Okay, OKAY. Personal space, freak!!"]},
 "poked.furious": {"any": ["THAT'S IT. Rude Mode fully engaged!!!"]},
 "clock.morning": {"any": ["Mornin'. ...Quit lookin' at me like I'm a morning person. I'm a MORNING MENACE."]},
 "clock.night": {"any": ["Night, huh. ...The dark's not so bad. Kinda cozy. Don't tell anyone I said that."]},
 "appLaunchGeneric": {"any": ["{app}, huh. It better be somethin' I can smash.", "{app}. ...Heh. Sounds like a warm-up."]},
 "coding": {"any": ["Typing stuff. Makin' the box do stuff. ...Y'know what, that's kinda metal."]},
 "gaming": {"any": ["A GAME?? Finally. Move over. I'll show ya how it's done. Violently."]},
 "batteryLow": {"any": ["Yo, your thing's dyin'. Even machines gotta rest. ...Heh. 'Rest.' Nerdy machine naps."]},
 "userReturned": {"any": ["Oh. You're back. ...I wasn't worried or nothin'. I was BORED. Different thing."]},
 "weather.rain": {"any": ["Rain!! Good. I was gettin' too dry. ...Monsters, y'know. Hydrate or... whatever."]},
 "weather.thunder": {"any": ["THUNDER!! HAH!! Sky's showin' off!! I respect that!!"]},
 "weather.snow": {"any": ["Snow. ...Snow's fine. What. Stop lookin' at me. I don't gotta justify enjoyin' SNOW."]},
 "dreading": {"any": ["Homework?! ...Alright, look. You do it, and I'll... supervotate. Aggressively."]},
 "hollowed": {"any": ["That knight bug?! They're TINY!! ...And they fight a whole kingdom?! ...Heh. Respect."]},
 "banter.respond": {"any": ["Quiet, ya nerd. ...I mean. Keep goin'. Whatever.", "HAH!! Nice one. ...I mean. It was OKAY.", "Kris!! You're... doin' fine or whatever."]},
})

ALL = {
 "dialogue_sans": SANS, "dialogue_papyrus": PAPYRUS, "dialogue_frisk": FRISK,
 "dialogue_flowey": FLOWEY, "dialogue_temmie": TEMMIE, "dialogue_monsterkid": MONSTERKID,
 "dialogue_annoyingdog": ANNOYINGDOG, "dialogue_niko": NIKO, "dialogue_knight": KNIGHT,
 "dialogue_hornet": HORNET, "dialogue_kris": KRIS, "dialogue_ralsei": RALSEI, "dialogue_susie": SUSIE,
}

for name, data in ALL.items():
    with open(OUT / f"{name}.json", "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    lines = sum(sum(len(v) for v in p.values()) for p in data.values())
    print(f"{name}: {len(data)} pools, {lines} canonical lines")
print("done")
