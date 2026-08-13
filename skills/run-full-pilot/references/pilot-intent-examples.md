# Pilot Intent Examples

Use meaning and conversational context, not keyword matching alone.

## Activate Pilot mode

These requests assign a clear outcome to the assistant:

- `Send this approved email to Maria.`
- `Schedule the supplier meeting for the agreed time.`
- `Update the CRM with today's confirmed appointments.`
- `Handle these follow-ups for me.`
- `Take care of everything needed to finish this.`
- `Use your best judgment and make it happen.`

State the inferred outcome in the preview and proceed within the task boundary.

## Stay in normal mode

These requests ask for thinking or preparation rather than external execution:

- `Draft an email to Maria.`
- `Review this message and tell me what you recommend.`
- `Prepare the meeting details.`
- `Research these suppliers and compare them.`
- `Show me the CRM changes before saving.`
- `What should I do next?`

Complete the useful preparation and stop before the external action.

## Explicit limit overrides action language

- `Draft this email and show me before sending.` → Draft only.
- `Prepare the campaign, but do not send it.` → Prepare only.
- `Schedule the meeting after I approve the time.` → Prepare and wait for the stated approval.

## Approval boundaries remain

- `Call Maria now.` → Pilot mode for the call, but wait for Jamaica to say **Ready** before dialing.
- `Email all 250 clients.` → Pilot mode for campaign preparation, but show the exact batch and wait for its required approval.
- `Buy the selected subscription.` → Pause because payment requires Jamaica.
- `Accept the supplier contract.` → Pause because legal acceptance requires Jamaica.
