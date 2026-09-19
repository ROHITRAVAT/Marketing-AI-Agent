import os

def fix_tools_for_analytics():
    with open("app/agents/nodes/tools.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
                    platform = (state.platform or "").lower()
                    if platform in ("linkedin", "facebook", "instagram", "twitter", "twitter/x"):
                        from app.models.scheduled_post import ScheduledPost
                        from datetime import datetime, timezone
                        
                        post_id = None
                        
                        if platform == "linkedin":
                            from app.services.linkedin_service import LinkedInService
                            async with AsyncSessionLocal() as db:
                                post_id = await LinkedInService.publish_post(
                                    user_id=state.user_id,
                                    content=content_body,
                                    db=db
                                )
                        elif platform == "facebook":
                            from app.services.facebook_service import FacebookService
                            async with AsyncSessionLocal() as db:
                                post_id = await FacebookService.publish_post(
                                    user_id=state.user_id,
                                    content=content_body,
                                    db=db
                                )
                        elif platform == "instagram":
                            from app.services.instagram_service import InstagramService
                            image_url = None
                            if state.generated_content and state.generated_content.metadata:
                                image_url = state.generated_content.metadata.get("image_url")
                            async with AsyncSessionLocal() as db:
                                post_id = await InstagramService.publish_post(
                                    user_id=state.user_id,
                                    content=content_body,
                                    image_url=image_url,
                                    db=db
                                )
                        elif platform in ("twitter", "twitter/x"):
                            from app.services.twitter_service import TwitterService
                            async with AsyncSessionLocal() as db:
                                post_id = await TwitterService.publish_post(
                                    user_id=state.user_id,
                                    content=content_body,
                                    db=db
                                )

                        # Create a ScheduledPost so analytics can track it!
                        image_url = None
                        if platform == "instagram" and state.generated_content and state.generated_content.metadata:
                            image_url = state.generated_content.metadata.get("image_url")
                        media_urls = [image_url] if image_url else None
                        
                        async with AsyncSessionLocal() as db:
                            new_post = ScheduledPost(
                                user_id=state.user_id,
                                platform="twitter" if platform == "twitter/x" else platform,
                                content=content_body,
                                media_urls=media_urls,
                                scheduled_time=datetime.now(timezone.utc),
                                status="published",
                                external_post_id=post_id,
                                published_at=datetime.now(timezone.utc),
                                approval_request_id=state.approval_request_id
                            )
                            db.add(new_post)
                            await db.commit()
                            await db.refresh(new_post)
                            db_post_id = new_post.id
                        
                        new_tool_results.append(
                            ToolResult(
                                tool_name=f"{platform}_publish",
                                status=ToolExecutionStatus.SUCCESS,
                                idempotency_key=idempotency_key,
                                data={"output": f"Post published successfully for {platform}. DB ID: {db_post_id} External ID: {post_id}"},
                            )
                        )
                    else:
"""
    
    # We will search for the code we added previously and replace it
    # We can just match `if platform in ("linkedin", "facebook", "instagram", "twitter", "twitter/x"):`
    # up to `else:`
    import re
    pattern = re.compile(r'                    platform = \(state\.platform or ""\)\.lower\(\).*?                    else:', re.DOTALL)
    
    content = pattern.sub(new_code.strip() + "\n                    else:", content)
    
    with open("app/agents/nodes/tools.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_tools_for_analytics()
