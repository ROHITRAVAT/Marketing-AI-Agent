import os

def fix_tools_py():
    with open("app/agents/nodes/tools.py", "r", encoding="utf-8") as f:
        content = f.read()

    new_code = """
                    platform = (state.platform or "").lower()
                    if platform in ("linkedin", "facebook", "instagram", "twitter", "twitter/x"):
                        from app.models.scheduled_post import ScheduledPost
                        from datetime import datetime, timezone, timedelta
                        
                        image_url = None
                        if platform == "instagram" and state.generated_content and state.generated_content.metadata:
                            image_url = state.generated_content.metadata.get("image_url")
                            
                        # Extract media URLs if any
                        media_urls = None
                        if image_url:
                            media_urls = [image_url]

                        async with AsyncSessionLocal() as db:
                            new_post = ScheduledPost(
                                user_id=state.user_id,
                                platform="twitter" if platform == "twitter/x" else platform,
                                content=content_body,
                                media_urls=media_urls,
                                scheduled_time=datetime.now(timezone.utc) + timedelta(minutes=5),
                                status="scheduled",
                                approval_request_id=state.approval_request_id
                            )
                            db.add(new_post)
                            await db.commit()
                            await db.refresh(new_post)
                            post_id = new_post.id
                        
                        new_tool_results.append(
                            ToolResult(
                                tool_name=f"{platform}_schedule",
                                status=ToolExecutionStatus.SUCCESS,
                                idempotency_key=idempotency_key,
                                data={"output": f"Post scheduled successfully for {platform}. Post ID: {post_id}"},
                            )
                        )
                    else:
"""
    
    old_code = """
                    platform = (state.platform or "").lower()
                    if platform == "linkedin":
                        from app.services.linkedin_service import LinkedInService
                        async with AsyncSessionLocal() as db:
                            post_id = await LinkedInService.publish_post(
                                user_id=state.user_id,
                                content=content_body,
                                db=db
                            )
                        
                        new_tool_results.append(
                            ToolResult(
                                tool_name="linkedin_publish",
                                status=ToolExecutionStatus.SUCCESS,
                                idempotency_key=idempotency_key,
                                data={"output": f"LinkedIn post published successfully. Post ID: {post_id}"},
                            )
                        )
                    elif platform == "facebook":
                        from app.services.facebook_service import FacebookService
                        async with AsyncSessionLocal() as db:
                            post_id = await FacebookService.publish_post(
                                user_id=state.user_id,
                                content=content_body,
                                db=db
                            )
                        
                        new_tool_results.append(
                            ToolResult(
                                tool_name="facebook_publish",
                                status=ToolExecutionStatus.SUCCESS,
                                idempotency_key=idempotency_key,
                                data={"output": f"Facebook post published successfully. Post ID: {post_id}"},
                            )
                        )
                    elif platform == "instagram":
                        from app.services.instagram_service import InstagramService
                        
                        # Extract image_url if provided by agent, else None (service uses placeholder)
                        image_url = None
                        if state.generated_content and state.generated_content.metadata:
                            image_url = state.generated_content.metadata.get("image_url")

                        async with AsyncSessionLocal() as db:
                            media_id = await InstagramService.publish_post(
                                user_id=state.user_id,
                                content=content_body,
                                image_url=image_url,
                                db=db
                            )
                        
                        new_tool_results.append(
                            ToolResult(
                                tool_name="instagram_publish",
                                status=ToolExecutionStatus.SUCCESS,
                                idempotency_key=idempotency_key,
                                data={"output": f"Instagram post published successfully. Media ID: {media_id}"},
                            )
                        )
                    elif platform in ("twitter", "twitter/x"):
                        from app.services.twitter_service import TwitterService
                        
                        async with AsyncSessionLocal() as db:
                            post_id = await TwitterService.publish_post(
                                user_id=state.user_id,
                                content=content_body,
                                db=db
                            )
                        
                        new_tool_results.append(
                            ToolResult(
                                tool_name="twitter_publish",
                                status=ToolExecutionStatus.SUCCESS,
                                idempotency_key=idempotency_key,
                                data={"output": f"Twitter post published successfully. Post ID: {post_id}"},
                            )
                        )
                    else:
"""
    
    if old_code.strip() in content:
        content = content.replace(old_code.strip(), new_code.strip())
    
    with open("app/agents/nodes/tools.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_tools_py()
