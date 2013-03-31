"""
Warning: this blog post expects you to know your email envelope recipient from your 'To' header address. If you don't, here's a good primer.

The company I currently work for sends out periodic mailouts to paying customers of our site. We comply with the CAN-SPAM act and give people a simple way to unsubscribe from our mailings, but some people still mark them as spam. This is a problem, because when people do this from the webmail interface of some ISPs, it records this, and if there are enough spam markings, starts refusing all connections from our mail servers until they process our removal request.

Many of the larger US ISPs allow you to sign up for an email 'feedback loop' where they notify you whenever they detect a 'spam' mail coming from your nominated IPs. We decided to try and use these feedback loops to automatically unsubscribe people from our mailing lists when they mark us as spam. There are two advantages:

We have a lower chance of getting unilaterally blocked by some ISPs,
People who don't want our messages won't get them.
All we need to do is pass the feedback loop messages to a script, extract the recipient address and send an unsubscribe request to the relevant part of our website. Sounds simple, right? I should be able to write something up using Python and procmail in an hour. Unfortunately life is a little more complex.

The first stumbling block is that most (all?) feedback loops remove some information from their notification emails. Of the two I've played with so far (AOL & Comcast), both remove the destination address. They don't do it sloppily either: every reference to the destination address is replaced with <redacted>. How can you tell who the message was sent to? In our case, we decided to modify our mailouts. Now, the envelope sender address we use in our mailouts includes a UID we can use to identify the sender. Previously our 'Return-Path' header looked like this:

Return-Path: <blah@ourdomain.com>
Now it looks like:

Return-Path: <blah+UID@ourdomain.com>
So now the feedback loop emails we get are useful! Next post I'll describe the simple procedure of parsing feedback loop emails with Python. If you want to skip ahead, here's a hint.
"""

"""
So we know what a feedback loop is and how to use it to identify customers complaining about our mails. The next step is to automate removal of these people.

It turns out many (most?) feedback loop emails you get from ISPs follow the same format. The message is made up of three sections:

The first section is a generic message from the feedback loop provider, "this is an email abuse report, yadda yadda yadda".
The second section is basically useless. It contains some information from the abuse report, but is usually heavily censored.
The third section is a copy of the original email you sent. Some information is redacted, like the recipient, and the sender address.
To process this we need two pieces of information:

Which ISP our feedback loop email comes from.
Who we sent the original email to.
This is relatively easy with Python, which includes the email library module and will do most of the heavy lifting for you.

The 'standard' feedback loop format is ARF, and is used by (at least) AOL, Comcast and Yahoo. To process an email in this format:
"""

import email
message = email.message_from_string(foo)

messagefrom = message['From'] # This is how you pull headers out.
                              # Note the keys are not case sensitive

messagebody = message.get_payload() # This returns three sections, as described above

originalmessage = messagebody[2].get_payload()[0] # This returns the original message.
                                       # We need to explicitly get the single payload.

originalmessagesender = originalmessage['Return-Path'] # Ta-da! The original sender.


"""
You can then process originalmessagesender as required to retrieve your UID. Once you have that, send a request through to the appropriate interface and you're done.

Bonus Notes

Some providers also strip the return path from the original message. We solved this by hand setting the message-id header on all outgoing mail. If you also do that, make sure you set each message-id to a unique value. We use the same string as our sender address, but change the generic '@noreply.ourcompany.com' domain to the real machine involved in sending and also include the output of time.time(), which gives us useful troubleshooting info too.
The original plan was to process feedback loop messages as they come in by spawning a script for every returned mail. This turned out to be a bad idea because abuse messages seem to come in bursts, making it possible we'd accidentally DOS our own mailserver with tens of python scripts. Now every feedback email will be delivered to a Maildir. We iterate over every message in the Maildir with Python's mailbox module (which returns an email object as above for each message).
If your feedback loop is in another format, it's pretty easy to work out the structure by playing with a sample message in the Python interpreter (IDLE).
"""
