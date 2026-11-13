import copy

def synthetic_workflow():
    names=['prompt','width','height','value_1','noise_seed','unet_name','clip_name','vae_name','vae_name_1','attention']
    values=['<Picture 1> is a storyboard. <Picture 2> is a missing sheet. Timeline 00:00–00:15.',640,384,5,1,'fastvideo_fasth3_8step_v2_pruned_int8_convrot.safetensors','example_encoder.safetensors','example_video_vae.safetensors','example_audio_vae.safetensors','example_attention']
    inputs=[{'name':'first_frame','link':1},{'name':'last_frame','link':None}]+[{'name':name,'widget':{'name':name},'link':None} for name in names]
    return {'nodes':[{'id':105,'type':'SYNTHETIC_TEST_GROUP','inputs':inputs,'widgets_values':values,'widgets_values_named':dict(zip(names,values))},{'id':136,'type':'LoadImage','widgets_values':['synthetic_test_frame.png','image']}],'links':[[1,136,0,105,0,'IMAGE']],'definitions':{'subgraphs':[{'id':'SYNTHETIC_TEST_GROUP','nodes':[{'id':104,'type':'MiniMaxH3ImageToVideo','widgets_values_named':{'prompt':'INTERNAL DEMO MUST NOT OVERRIDE GROUP'}},{'id':6,'type':'UNETLoader','widgets_values':['example.safetensors','default']}]}]}}
