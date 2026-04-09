from huggingface_hub import InferenceClient
from modules.meeting_summarizer import SYSTEM_PROMPT

HF_TOKEN = "YOUR_HF_TOKEN"
client = InferenceClient(token=HF_TOKEN)

def summarize_transcript(transcript_text: str) -> str:
    import re
    response = client.chat_completion(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Please summarize this transcript:\n\n{transcript_text}"}
        ],
        max_tokens=2000,
        temperature=0.3,
    )
    result = response.choices[0].message.content
    result = re.sub(r'═{3,}.*\n?', '', result)
    result = re.sub(r'FORMAT FOR TYPE [AB].*\n?', '', result)
    return result.strip()

if __name__ == "__main__":
    # The transcript you provided
    transcript = """
T S AVISH
0 240:24
T S AVISH 0 minutes 24 seconds
Good morning everyone. This is my Python project on hostel complaint registration and automated e-mail system. As the topic says, I've built the radio based application on hostel complaint management.
T S AVISH 0 minutes 42 seconds
My objectives are giving a digital platform for hostile complaints and tracking the process and management in real time. So the manual what is the problem? Why you are getting into objective tab?
T S AVISH 1 minute
In manual complaint handling there was there will be lose of data and the progress of the complaint tracking will not happen.
T S AVISH 1 minute 12 seconds
Not happen correctly, so there is a lack of transparency so they can show that the progress is completed even when there is no.
T S AVISH 1 minute 25 seconds
Even when there is no problem solved, so communication between students also becomes slow and everything you have written only no without seeing only.
T S AVISH 1 minute 39 seconds
See.
T S AVISH 1 minute 40 seconds
Improve in communication, improve in sales VNS.
T S AVISH 1 minute 46 seconds
That is what the same feedback she have given to you. Have you read the comments or you skipped it? Only one comment she only one comment in that there was a eight points I'll show you.
T S AVISH 2 minutes 2 seconds
Photo slide view.
T S AVISH 2 minutes 4 seconds
Then you're not getting any lavish.
T S AVISH 38 minutes 48 seconds
When you enter your mail ID or your name, this mail ID no one will remember. What is the point of mail ID?
T S AVISH 38 minutes 55 seconds
Room number is not there. From where they will capture the room. The room number. It can be given in description while while student. What if now you haven't given now how they will close it?
T S AVISH 39 minutes 9 seconds
I'm running classroom, which classroom, which blog, everywhere is a classroom, you know.
T S AVISH 39 minutes 15 seconds
That is losing major.
T S AVISH 39 minutes 18 seconds
Room number has to be closed, correct? There'll be no number. Which block is must? Where is the block number?
T S AVISH 39 minutes 25 seconds
Name of the block is missing. The room is missing. Your name only is Rasul. Those are all not there in REVA. Why you think REVA do for some other organization when you do for the CMR?
T S AVISH 39 minutes 44 seconds
So Google president will sell your product. Yeah, PG, PG. You can sell it to the PG, normal PG. Your product should come in that way. Can you sell this still improvements?
T S AVISH 40 minutes
You give me this idea how to say.
T S AVISH 40 minutes 4 seconds
Corrections you do 100 times, corrections will be there only. They cannot stop your door with the corrections.
T S AVISH 40 minutes 12 seconds
We haven't done the work and there is no confidence means.
T S AVISH 40 minutes 18 seconds
So set with Sai. Sai will give us experience. Let's listen to him improve on it before POD from all the details should be there. Log name should be if you're doing only for Reva, how many blocks are there?
T S AVISH 40 minutes 33 seconds
One blocks, only four blocks invoice, but it's not uh.
T S AVISH 40 minutes 43 seconds
If you're really or no, why are you generalizing? I don't know about you asked with the Chinese. Chinese you stay in Australia. No, how many blocks are there?
T S AVISH 40 minutes 56 seconds
G1 is there, G2 is there, G3 or four plus 37 and only 7 block. G1 block, G2G3 in G1, how many rooms are there? That will have to be known in C block. How many floors are there? Which now how many room now capacities are there?
T S AVISH 41 minutes 16 seconds
That details may be a groundwork.
T S AVISH 41 minutes 21 seconds
Why is also D block is the biggest one? How many rooms are there in the D block?
T S AVISH 41 minutes 26 seconds
Yeah.
T S AVISH 41 minutes 28 seconds
That is in same block around 400, three 400 rooms.
T S AVISH 41 minutes 39 seconds
So what I mean 4 means you know yeah it's 400 members you would have seen in that notice board that is 400 members not room in the one node you might see around 15 to 1694 one second.
T S AVISH 41 minutes 55 seconds
I say, yeah, I remember 16 or something close that you only should do it now.
T S AVISH 42 minutes 6 seconds
Or randomly put not that in this particular block we have so many rooms. They should enter the room number. You should validate what if my room number I'm giving as a 1005. There's no room number like that only. Correct application is not there.
T S AVISH 42 minutes 23 seconds
I am seeing. It was there.
T S AVISH 42 minutes 28 seconds
Or when they give a room number to me with my name, by automatically the room number will be freezed over there. When I enter average, it will show you you block, it belongs to the C block, room number 405 will show you that.
"""
    
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("Sending transcript to Hugging Face...")
    summary_output = summarize_transcript(transcript)
    print("\n--- Output ---\n")
    print(summary_output)
    
    # Also save to file
    with open("summary_output.md", "w", encoding="utf-8") as f:
        f.write(summary_output)
    print("\nSummary saved to summary_output.md")
